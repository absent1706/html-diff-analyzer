# HTML-diff-analyzer

CLI tool for finding tags in sample files
  which are most similar to tag with given id in origin file.

Usage guide:
```
    python html-diff-analyzer.py -h
```

Usage example (demo files):
```
    python html-diff-analyzer.py demo-files/sample-0-origin.html demo-files/sample-1-evil-gemini.html
    python html-diff-analyzer.py demo-files/sample-0-origin.html demo-files/sample-2-container-and-clone.html
    python html-diff-analyzer.py demo-files/sample-0-origin.html demo-files/sample-3-the-escape.html
    python html-diff-analyzer.py demo-files/sample-0-origin.html demo-files/sample-4-the-mash.html
```
