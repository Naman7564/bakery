pipeline {
    agent any

    stages {
        stage('Code') {
            steps {
                echo "Code Clone Stage"
                git branch: 'main',
                    url: 'https://github.com/Naman7564/bakery.git'
            }
        }

        stage('Build') {
            steps {
                echo "Code Build Stage"
                sh "docker build -t bakery:latest ."
            }
        }

        stage('Test') {
            steps {
                echo 'Running Tests...'
                sh "docker run --rm bakery:latest python manage.py test"
            }
        }

        stage("Push To DockerHub") {
            steps {
                echo "Pushing to Docker Hub"
            }
        }

        stage('Backup') {
            steps {
                echo "Creating Backup..."
                sh "docker tag bakery:latest bakery:backup"
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sh "docker compose down && docker compose up -d"
            }
        }
    }

    post {
        failure {
            echo "Deployment failed! Rolling back..."
            sh "docker tag bakery:backup bakery:latest"
            sh "docker compose down && docker compose up -d"
        }
    }
}