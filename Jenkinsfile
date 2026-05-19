pipeline {
    agent any

    environment {
        DATABRICKS_HOST       = credentials('databricks-host')
        DATABRICKS_TOKEN      = credentials('databricks-token')
        AZURE_CLIENT_ID       = credentials('azure-client-id')
        AZURE_CLIENT_SECRET   = credentials('azure-client-secret')
        AZURE_TENANT_ID       = credentials('azure-tenant-id')
        AZURE_STORAGE_ACCOUNT = credentials('azure-storage-account')
        ADF_RESOURCE_GROUP    = 'sales-resource-group'
        ADF_NAME              = 'vssales-adf'
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/vishnu0111/sales-pipeline-project.git'
                echo 'Code checkout done'
            }
        }

        stage('Code Quality Check') {
            steps {
                bat '''
                pip install flake8
                flake8 databricks/ --max-line-length=100
                '''
                echo 'Linting passed'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat '''
                pip install pytest pyspark
                pytest tests/ -v
                '''
                echo 'Unit tests passed'
            }
        }

        stage('Deploy Notebooks to Databricks') {
            steps {
                bat '''
                pip install databricks-cli
                echo %DATABRICKS_HOST%> host.txt
                echo %DATABRICKS_TOKEN%>> host.txt
                databricks configure --token < host.txt
                del host.txt
                databricks workspace import_dir databricks/notebooks /Shared --overwrite
                '''
                echo 'Notebooks deployed to Databricks'
            }
        }

        stage('Deploy ADF Pipeline') {
            steps {
                bat '''
                az login --service-principal ^
                    -u %AZURE_CLIENT_ID% ^
                    -p %AZURE_CLIENT_SECRET% ^
                    --tenant %AZURE_TENANT_ID%

                az datafactory pipeline create ^
                    --resource-group %ADF_RESOURCE_GROUP% ^
                    --factory-name %ADF_NAME% ^
                    --name pipeline_sales_ingest ^
                    --pipeline @adf/arm_templates/pipeline_sales_ingest.json
                '''
                echo 'ADF Pipeline deployed'
            }
        }

        stage('Trigger ADF Pipeline') {
            steps {
                bat '''
                az datafactory pipeline create-run ^
                    --resource-group %ADF_RESOURCE_GROUP% ^
                    --factory-name %ADF_NAME% ^
                    --name pipeline_sales_ingest
                '''
                echo 'ADF Pipeline triggered!'
            }
        }

    }

    post {
        success {
            echo 'All stages completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs.'
        }
    }
}