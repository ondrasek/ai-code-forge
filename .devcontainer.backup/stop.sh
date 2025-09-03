docker stop $(docker ps --filter "label=my.repositoryName=$(gh repo view --json name -q '.name')" --format "{{.ID}}") 
