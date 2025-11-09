pipeline {
    agent any

    environment {
        WEBEX_BOT_TOKEN = credentials('WEBEX_BOT_TOKEN')
        WEBEX_ROOM_ID = credentials('WEBEX_ROOM_ID')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<your-username>/cicd-webex.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh 'apt-get update && apt-get install -y python3 python3-pip python3-venv'
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest -v'
            }
        }

        stage('Notify WebEx') {
            steps {
                script {
                    def message = " Jenkins build successful for *cicd-webex* calculator project!"
                    sh """
                    curl -X POST \
                        -H "Authorization: Bearer ${WEBEX_BOT_TOKEN}" \
                        -H "Content-Type: application/json" \
                        -d '{"roomId": "${WEBEX_ROOM_ID}", "markdown": "${message}"}' \
                        https://webexapis.com/v1/messages
                    """
                }
            }
        }
    }

    post {
        failure {
            script {
                def message = " Jenkins build failed for *cicd-webex* calculator project."
                sh """
                curl -X POST \
                    -H "Authorization: Bearer ${WEBEX_BOT_TOKEN}" \
                    -H "Content-Type: application/json" \
                    -d '{"roomId": "${WEBEX_ROOM_ID}", "markdown": "${message}"}' \
                    https://webexapis.com/v1/messages
                """
            }
        }
    }
}
