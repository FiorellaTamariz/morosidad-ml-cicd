pipeline {
    agent any

    environment {
        IMAGE_NAME     = "morosidad-api"
        TEST_CONTAINER = "morosidad-test"
        PROD_CONTAINER = "morosidad-prod"

        // Usa la instalación de Python configurada en Jenkins
        PY = "${tool 'Python3'}\\python.exe"
        PIP = "${tool 'Python3'}\\python.exe -m pip"
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
                    %PY% -m pip install --upgrade pip
                    %PY% -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                echo "Ejecutando tests..."
                bat "%PY% -m pytest tests/ -v"
            }
        }

        stage('Train Model') {
            steps {
                echo "Entrenando modelo..."
                bat "%PY% src/train.py"
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
                    docker stop %TEST_CONTAINER% || exit 0
                    docker rm %TEST_CONTAINER% || exit 0
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
                    docker stop %PROD_CONTAINER% || exit 0
                    docker rm %PROD_CONTAINER% || exit 0
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
