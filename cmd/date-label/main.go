package main

import (
	"flag"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"

	"github.com/otiai10/copy"
)

var issues []string   // A list of the directory names of the issues
var issueIdx int = -1 // Keeps track of what issues have already been processed.
var inputDir string   // The directory that contains the issue folders
var outputDir string  // The directory to place the folders labelled by date

func check(err error) {
	if err != nil {
		fmt.Printf("Error : %s\n", err.Error())
		os.Exit(1)
	}
}

type PageData struct {
	PdfPath string
}

func getIssue() string {
	issueIdx++
	issue := issues[issueIdx]
	return issue
}

func servePdf(w http.ResponseWriter, r *http.Request) {
	if issueIdx >= len(issues) {
		// If there are no more issues to label
		fmt.Fprintf(w, "Labelling complete")
		os.Exit(0)
	}
	tmpl, _ := template.ParseFiles("web/layout.html")
	issue := getIssue()
	data := PageData{PdfPath: issue}
	tmpl.Execute(w, data)
}

func copyIssue(date string) {
	sourceDir := path.Join(inputDir, issues[issueIdx])
	destDir := path.Join(outputDir, date)
	copy.Copy(sourceDir, destDir)
	log.Printf("Copied %s to %s\n", sourceDir, destDir)
}

func home(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.Error(w, "404 not found.", http.StatusNotFound)
		return
	}

	switch r.Method {
	case "GET":
		servePdf(w, r)
	case "POST":
		if err := r.ParseForm(); err != nil {
			fmt.Fprintf(w, "ParseForm() err: %v", err)
			return
		}
		date := r.FormValue("date")
		copyIssue(date)
		servePdf(w, r)
	default:
		fmt.Fprintf(w, "Sorry, only GET and POST methods are supported.")
	}
}

func get_issues(inputDir string) {
	objs, err := ioutil.ReadDir(inputDir)
	check(err)
	for _, f := range objs {
		if !f.IsDir() {
			continue
		}
		issues = append(issues, f.Name())
	}
}

func processFlags() {
	// Get the directory of the split pdfs as a commandline flag and verify it's a valid dir
	var inputDirPtr = flag.String("in-dir", "", "Directory of the split pdfs")
	var outputDirPtr = flag.String("out-dir", "", "Output directory")
	flag.Parse()
	inputDir = *inputDirPtr
	outputDir = *outputDirPtr
	if _, err := os.Stat(inputDir); os.IsNotExist(err) {
		msg := fmt.Sprintf("Path '%s' does not exist\n", inputDir)
		log.Fatal(msg)
		os.Exit(1)
	}
	get_issues(inputDir)
}

func main() {
	processFlags()
	http.HandleFunc("/", home)
	http.Handle("/scans/", http.StripPrefix("/scans/", http.FileServer(http.Dir(inputDir))))
	fmt.Printf("Starting server at http://localhost:8080\n")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
