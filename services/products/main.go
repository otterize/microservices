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

// Load products from the JSON file
func loadProducts(client *s3.Client) {
	mu.Lock()
	defer mu.Unlock()

	var data []byte
	var err error

	if BucketEnabled == "true" {
		log.Printf("Loading products from S3 bucket: %s\n", BucketName)

		input := &s3.GetObjectInput{
			Bucket: aws.String(BucketName),
			Key:    aws.String(ObjectKey),
		}

		result, err := client.GetObject(context.TODO(), input)
		if err != nil {
			log.Printf("Failed to get object from S3: %v\n", err)
			return
		}
		defer result.Body.Close()

		data, err = ioutil.ReadAll(result.Body)
		if err != nil {
			log.Printf("Failed to read S3 object body: %v\n", err)
			return
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

func reloadProductData(client *s3.Client) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		loadProducts(client)
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

	// Load products
	loadProducts(s3Client)
	go reloadProductData(s3Client)

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
