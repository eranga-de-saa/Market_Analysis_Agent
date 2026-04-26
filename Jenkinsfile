pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "my-market-analysis-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:latest ."
            }
        }

        // stage('Test') {
        //     steps {
        //         // Example: Running a python test inside the built image
        //         sh "docker run --rm ${DOCKER_IMAGE}:latest pytest src/tests"
        //     }
        // }

        stage('Deploy') {
            steps {
                // Restarts only the 'app' service in your compose stack
                sh "docker-compose up -d --build app"
            }
        }
    }
}