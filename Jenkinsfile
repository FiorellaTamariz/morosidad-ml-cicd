pipeline {
    agent any

    environment {
        IMAGE_NAME = "morosidad-api"
        TEST_CONTAINER = "morosidad-test"
        PROD_CONTAINER = "morosidad-prod"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Clonando repositorio..."
                checkout scm
            }
        }

        stage('Install Python Dependencies') {
            steps {
                echo "Instalando dependencias..."
                bat """
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                echo "Ejecutando tests..."
                bat "pytest tests/ -v"
            }
        }

        stage('Train Model') {
            steps {
                echo "Entrenando modelo..."
                bat "python src/train.py"
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Construyendo imagen Docker..."
                bat "docker build -t %IMAGE_NAME%:latest ."
            }
        }

        stage('Test Container') {
            steps {
                echo "Probando contenedor..."
                bat """
                    docker stop %TEST_CONTAINER% || true
                    docker rm %TEST_CONTAINER% || true
                    docker run -d --name %TEST_CONTAINER% -p 5001:5000 %IMAGE_NAME%:latest
                    ping -n 10 127.0.0.1 >NUL
                    curl -f http://localhost:5001/health
                """
            }
        }

        stage('Deploy') {
            steps {
                echo "Desplegando contenedor en producción..."
                bat """
                    docker stop %PROD_CONTAINER% || true
                    docker rm %PROD_CONTAINER% || true
                    docker run -d --name %PROD_CONTAINER% -p 5000:5000 %IMAGE_NAME%:latest
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline completado con éxito."
        }
        failure {
            echo "Pipeline falló."
        }
    }
}
