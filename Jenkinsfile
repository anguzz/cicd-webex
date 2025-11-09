pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/anguzz/cicd-webex.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                apt-get update -y
                apt-get install -y python3 python3-pip python3-venv
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate && pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate && pytest -v || true
                '''
            }
        }

        stage('Notify WebEx - Success') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
                    string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
                ]) {
                    sh '''
                    curl -X POST \
                      -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                      -H "Content-Type: application/json" \
                      -d "{\"roomId\": \"$WEBEX_ROOM_ID\", \"markdown\": \" Jenkins build successful for *cicd-webex* calculator project!\"}" \
                      https://webexapis.com/v1/messages
                    '''
                }
            }
        }
    }

    post {
        failure {
            withCredentials([
                string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
                string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
            ]) {
                sh '''
                curl -X POST \
                  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                  -H "Content-Type: application/json" \
                  -d "{\"roomId\": \"$WEBEX_ROOM_ID\", \"markdown\": \" Jenkins build failed for *cicd-webex* calculator project.\"}" \
                  https://webexapis.com/v1/messages
                '''
            }
        }
    }
}
