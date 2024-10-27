package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gorilla/mux"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"log"
	"net/http"
	"os"
)

// User struct - GORM will map this struct to the 'users' table
type User struct {
	ID       uint   `json:"id" gorm:"primaryKey"`
	Email    string `json:"email" gorm:"unique"`
	Password string `json:"password"`
}

// Database connection (global variable for simplicity)
var db *gorm.DB

var DbName = getEnv("DB_NAME", "otterside")
var DbServiceHost = getEnv("DB_SERVICE_HOST", "localhost")
var DbServiceUser = getEnv("DB_SERVICE_USER", "postgres")
var DbServicePass = getEnv("DB_SERVICE_PASS", "password")

// Initialize database and create the users table
func initDB() {
	var err error
	// Postgres connection URL (update with your Postgres details)
	dsn := fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=5432 sslmode=disable",
		DbServiceHost,
		DbServiceUser,
		DbServicePass,
		DbName,
	)
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Migrate the schema (create Users table if it doesn't exist)
	db.AutoMigrate(&User{})
	fmt.Println("Database connected and Users table migrated.")
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

// Handler for signing up new users (POST /signup)
func signUpHandler(w http.ResponseWriter, r *http.Request) {
	var user User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil || user.Email == "" || user.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Check if user exists
	var existingUser User
	if err := db.Where("email = ?", user.Email).First(&existingUser).Error; err == nil {
		http.Error(w, "User already exists", http.StatusConflict)
		return
	}

	// Create user in the database
	if result := db.Create(&user); result.Error != nil {
		http.Error(w, "Failed to create user", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"message": "User created successfully!"})
}

// Handler for signing in (POST /signin)
func signInHandler(w http.ResponseWriter, r *http.Request) {
	var input User
	err := json.NewDecoder(r.Body).Decode(&input)
	if err != nil || input.Email == "" || input.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var user User
	// Check if user exists and password matches
	if err := db.Where("email = ? AND password = ?", input.Email, input.Password).First(&user).Error; err != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	// Return user details
	json.NewEncoder(w).Encode(map[string]interface{}{
		"id":    user.ID,
		"email": user.Email,
	})
}

// Handler for getting logged-in user data (GET /me)
// Note: For simplicity, user email is passed in the query params, no auth token is used.
func getUserHandler(w http.ResponseWriter, r *http.Request) {
	email := r.URL.Query().Get("email")
	if email == "" {
		http.Error(w, "Email is required", http.StatusBadRequest)
		return
	}

	var user User
	if err := db.Where("email = ?", email).First(&user).Error; err != nil {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	// Return user details
	json.NewEncoder(w).Encode(map[string]interface{}{
		"id":    user.ID,
		"email": user.Email,
	})
}

func main() {
	// Initialize the database and create tables
	initDB()

	// Setup router and routes
	r := mux.NewRouter()

	r.HandleFunc("/signup", signUpHandler).Methods("POST")
	r.HandleFunc("/signin", signInHandler).Methods("POST")
	r.HandleFunc("/me", getUserHandler).Methods("GET")

	// Start the server
	fmt.Println("Server is running on port 7001...")

	if _, err := os.Stat("server.crt"); errors.Is(err, os.ErrNotExist) {
		log.Fatal(http.ListenAndServe(":7001", r))
	} else {
		log.Fatal(http.ListenAndServeTLS(":7001", "server.crt", "server.key", r))
	}
}
