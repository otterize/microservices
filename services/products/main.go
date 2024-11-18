package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/gorilla/mux"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/aws/aws-sdk-go-v2/config"
)

type Product struct {
	ID       int     `json:"id"`
	Title    string  `json:"title"`
	Image    string  `json:"image"`
	Category string  `json:"category"`
	Price    float64 `json:"price"`
}

var products []Product
var mu sync.Mutex // Mutex for thread-safe access to products

var BucketEnabled = getEnv("STORAGE_ENABLED", "true")
var BucketRegion = getEnv("STORAGE_REGION", "us-east-1")
var BucketName = getEnv("STORAGE_BUCKET_NAME", "otterside")
var ObjectKey = getEnv("STORAGE_OBJECT_KEY", "products.json")

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func readAzureBlob(client *azblob.Client) ([]byte, error) {
	log.Printf("Loading products from Azure container: %s\n", BucketName)

	// Download the blob content
	resp, err := client.DownloadStream(context.TODO(), BucketName, ObjectKey, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to download blob: %w", err)
	}
	defer resp.Body.Close()

	return ioutil.ReadAll(resp.Body)
}

func readS3Object(client *s3.Client) ([]byte, error) {
	log.Printf("Loading products from S3 bucket: %s\n", BucketName)

	input := &s3.GetObjectInput{
		Bucket: aws.String(BucketName),
		Key:    aws.String(ObjectKey),
	}

	result, err := client.GetObject(context.TODO(), input)
	if err != nil {
		return nil, fmt.Errorf("Failed to get object from S3: %v\n", err)
	}
	defer result.Body.Close()

	return ioutil.ReadAll(result.Body)
}

// Load products from the JSON file
func loadProducts(s3Client *s3.Client, blobClient *azblob.Client) {
	mu.Lock()
	defer mu.Unlock()

	var data []byte
	var err error

	if BucketEnabled == "true" {
		data, err = readS3Object(s3Client)
		if err != nil {
			log.Fatalf("Failed to read aws products.json: %v", err)
		}

		data, err = readAzureBlob(blobClient)
		if err != nil {
			log.Fatalf("Failed to read azure products.json: %v", err)
		}
	} else {
		log.Printf("Loading products from filesystem: %s\n", ObjectKey)

		data, err = ioutil.ReadFile(ObjectKey)
		if err != nil {
			log.Fatalf("Failed to read products.json: %v", err)
		}
	}

	if err = json.Unmarshal(data, &products); err != nil {
		log.Fatalf("Failed to unmarshal JSON: %v", err)
	}
}

func reloadProductData(client *s3.Client, blobClient *azblob.Client) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		loadProducts(client, blobClient)
	}
}

// Get all products
func getProducts(w http.ResponseWriter, r *http.Request) {
	log.Println("Getting all products")
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(products)
}

// Get product by ID
func getProductByID(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	id, err := strconv.Atoi(params["id"])
	if err != nil {
		http.Error(w, "Invalid product ID", http.StatusBadRequest)
		return
	}
	log.Printf("Getting product by ID: %d \n", id)

	for _, product := range products {
		if product.ID == id {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(product)
			return
		}
	}

	http.Error(w, "Product not found", http.StatusNotFound)
}

func main() {
	// Initialize AWS SDK for S3
	cfg, err := config.LoadDefaultConfig(
		context.TODO(),
		config.WithRegion(BucketRegion),
		config.WithCredentialsProvider(aws.AnonymousCredentials{}),
	)
	if err != nil {
		log.Fatalf("Unable to load AWS SDK config: %v", err)
	}
	s3Client := s3.NewFromConfig(cfg)

	// Initialize Azure SDK for Blob Storage
	blobClient, err := azblob.NewClientWithNoCredential("https://ottersidestorage.blob.core.windows.net", nil)
	if err != nil {
		log.Fatalf("Unable to load AWS SDK config: %v", err)
	}

	// Load products
	loadProducts(s3Client, blobClient)
	go reloadProductData(s3Client, blobClient)

	// Set up the router
	r := mux.NewRouter()

	// Define routes
	r.HandleFunc("/products", getProducts).Methods("GET")
	r.HandleFunc("/products/{id}", getProductByID).Methods("GET")

	// Start the server
	fmt.Println("Server running on http://localhost:7002")

	if _, err := os.Stat("server.crt"); errors.Is(err, os.ErrNotExist) {
		log.Fatal(http.ListenAndServe(":7002", r))
	} else {
		log.Fatal(http.ListenAndServeTLS(":7002", "server.crt", "server.key", r))
	}
}
