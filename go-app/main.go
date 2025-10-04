package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os/exec"

	_ "github.com/lib/pq"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Insecure Go app")
	})

	http.HandleFunc("/query", func(w http.ResponseWriter, r *http.Request) {
		user := r.URL.Query().Get("user")
		db, err := sql.Open("postgres", "postgres://admin:admin@localhost/insecure?sslmode=disable")
		if err != nil {
			fmt.Fprintln(w, err)
			return
		}
		defer db.Close()
		query := fmt.Sprintf("SELECT * FROM users WHERE username = '%s'", user)
		rows, err := db.Query(query)
		if err != nil {
			fmt.Fprintln(w, err)
			return
		}
		defer rows.Close()
		fmt.Fprintf(w, "Executed query: %s", query)
	})

	http.HandleFunc("/exec", func(w http.ResponseWriter, r *http.Request) {
		cmd := r.URL.Query().Get("cmd")
		out, err := exec.Command("/bin/sh", "-c", cmd).CombinedOutput()
		if err != nil {
			fmt.Fprintf(w, "error: %s\n", err)
		}
		w.Write(out)
	})

	log.Fatal(http.ListenAndServe(":9090", nil))
}
