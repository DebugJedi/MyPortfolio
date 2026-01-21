PROJECT_ID=myportfolio-445218

gcloud builds submit \
    --tag us-west1-docker.pkg.dev/$PROJECT_ID/portfolio/portfolioimg \
    --project $PROJECT_ID