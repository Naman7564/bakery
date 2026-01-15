@Library('shared-pipeline-library') _

pipeline {
    agent {
        label 'doraemon'
    }

    stages {
        stage('Code') {
            steps {
                echo "Code Clone Stage"
                git branch: 'main',
                    url: 'https://github.com/Naman7564/bakery.git'
            }
        }

        stage('Backup') {
            steps {
                echo "Creating Backup of Previous Image..."
                dockerBackup()
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

        stage('Push To DockerHub') {
            steps {
                echo "Pushing to Docker Hub"
                docker_push("bakery", "naman7564", "latest")
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
            dockerRollback()
        }
    }
}
