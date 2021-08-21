# GCP Qwiklabs Quests for Machine Learning Engineers

## SSH commands
- Use ```touch```, ```nano```, and ```cat``` to create, edit and output the contents of files.  
- ```./XXX.sh```  
- Get root access:```sudo su -``` 
- As the root user, update your OS:```apt-get update```   
- Install NGINX (one of the most widely used web servers in the world):```apt-get install nginx -y``` in order to connect my VM to something through it.  
- Confirm NGINX is running:```ps auwx | grep nginx```  

## Takeaways from Qwiklab
- How to use [DataFlow](https://google.qwiklabs.com/focuses/1101?parent=catalog) templates to create a streaming pipeline
- How to use [DataPrep](https://google.qwiklabs.com/focuses/584?parent=catalog) to visually explore, clean, prepare data from analysis. Quite like Tableau, can do pivot, filter, and more for data analysis.
- How to use [Google Data Studio](https://run.qwiklabs.com/focuses/3614?parent=catalog) to create dashboards and reports like in Tableau.
- How to use [AI Platform](https://google.qwiklabs.com/focuses/581?parent=catalog) > Notebooks and terminal command-line prompt to train, test data and predict using the trained model locally and deploy on the cloud. The example is a binary classification model using a Keras Sequential model.
- How to use [DataProc](https://google.qwiklabs.com/focuses/585?parent=catalog) to run Apache Spark and Hadoop cluster through console and command-line prompt.
- How to use [Cloud Natural Language API](https://google.qwiklabs.com/focuses/582?parent=catalog) to perform POS tag, sentimental analysis, NER, and content classification.
- How to use [Cloud Speech API](https://google.qwiklabs.com/focuses/588?parent=catalog) to convert audio into text transcription both synchronously and asynchronously, meaning you can send a complete audio file, but you can also use synchronous method to perform streaming speech to text transcription while the user is still speaking.  
- How to use [Google Kubernetes Engine (GKE)](https://google.qwiklabs.com/focuses/878?parent=catalog) to deploy, manage, and scale containerized applications. The Kubernetes Engine environment consists of multiple machines (specifically Compute Engine instances) grouped to form a container cluster.
- How to use [BigQuery](https://run.qwiklabs.com/focuses/2802?parent=catalog) to 
  1. Manage databases (similar to MySQL), query keywords and export subsets of the original dataset into CSV files, and then upload to Cloud SQL.
    - Use GROUP BY to output the unique column values found in the table.
    - Use COUNT() to return the number of rows that share the same criteria (e.g. column value). This can be very useful in tandem with a GROUP BY.
    - Use AS to create an alias of a table or column. An alias is a new name that's given to the returned column or table.
    - Use UNNEST to take elements in an array and expand each one ot these individual elements.
    - Examine the schema of a table in the samples dataset: ```bq show bigquery-public-data:samples.<table_name>```
    - Delete a dataset: ```bq rm -r <dataset_name>```
  2. Create and Excute machine learning models in BigQuery using SQL queries ([BQML](https://google.qwiklabs.com/focuses/2157?parent=catalog)). Use cases: 
    - Preprocess ecommerce data and [predict visitor purchases with a classification model](https://google.qwiklabs.com/focuses/1794?parent=catalog) **Classification**
    - Explore millions of New York City yellow taxi cab trips and [predict the fare of the cab ride](https://google.qwiklabs.com/focuses/1797?parent=catalog). **Regression**
    - Predict [NCAA tournament winners](https://google.qwiklabs.com/focuses/4337?parent=catalog) and learn about feature weight by SQL scripts.
    - Deploy a [chatbot application using Dialogflow](https://google.qwiklabs.com/focuses/4414?parent=catalog), more specifically, use an inline code editor within Dialogflow for deloying a Node.js fulfillment script that integrates BigQuery.

## Cloud Shell Console Command-line prompts
- Create a json file and add a FLAC audio file stored in Google Could Storage to it through shh command-line prompt:
```
cat > request.json <<EOF
{
  "config": {
      "encoding":"FLAC",
      "languageCode": "en-US"
  },
  "audio": {
      "uri":"gs://cloud-training/gsp323/task4.flac"
  }
}
EOF
```
- Upload the analyzed result of ML models to Google Cloud Data Storage:  
  1. ```gcloud auth login```  
  2. ```gsutil cp XX  gs:// YY```(XX is the instance name and YY is the bucket name.)  

- Use ```gcloud``` to connect to computing resources hosted on Google Cloud via Cloud Shell.  
- List the project ID:```gcloud config list project```  
- See the default zone setting:```gcloud config get-value compute/zone``` ;See the default region setting: ```gcloud config get-value compute/region``` ; Set compute zone: ```gcloud config set compute/zone <zone>
- Create an environment variable to store you Project ID:```export PROJECT_ID=<your_project_id>```  ; Verify the variable is set properly:```echo $PROJECT_ID``` 
- Create a VM: ```gcloud compute instances create <VM_name> --machine-type <machine_type> --zone <zone>
- Display guidlines: ```gcloud config --help``` or ```gcloud help config```. To exit, type Q.
- List all the configurations in your environment: ```gcloud config list```
- See all properties and their settings: ```gcloud config list --all```
- List all components: ```gcloud components list```; List all instances: ```gcloud compute instances list```
- Create a cluster: ```gcloud container clusters create <cluster_name>```; Authenticate the cluster: ```gcloud container clusters get-credentials <cluster_name>```; Delete a cluster: ```gcloud container clusters delete <cluster_name>```
- Connect the Cloud Shell to your SQL instance: ```gcloud sql connect <instance_name> --user=root```


The pop method copies and removes the label column from the dataframe:```train_x, train_y = train_df, train_df.pop(_LABEL_COLUMN)```



