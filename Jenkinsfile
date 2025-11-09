pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root'
        }
    }

    environment {
        VENV_DIR = 'venv'
        PYTEST_SUMMARY = ''
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/anguzz/cicd-webex.git'
            }
        }

        stage('Check Python') {
            steps {
                sh '''
                echo "Checking Python installation..."
                python3 --version
                pip --version
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                python3 -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests, log output, and continue even on failure
                    sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v | tee pytest_output.txt || true
                    '''

                    // Capture the last 5 lines of pytest output for WebEx summary
                    env.PYTEST_SUMMARY = sh(
                        script: "tail -n 5 pytest_output.txt || echo 'No test summary found.'",
                        returnStdout: true
                    ).trim()
                }
            }
        }
    }

    post {
        success {
            withCredentials([
                string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
                string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
            ]) {
                sh """
                curl -s -X POST \
                  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                  -H "Content-Type: application/json" \
                  -d "{\\"roomId\\": \\"$WEBEX_ROOM_ID\\", \\"markdown\\": \\" Jenkins build successful for *cicd-webex* project!\\n\\n**Test Summary:**\\n${env.PYTEST_SUMMARY}\\"}" \
                  https://webexapis.com/v1/messages
                """
            }
        }

        failure {
            withCredentials([
                string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
                string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
            ]) {
                sh """
                curl -s -X POST \
                  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                  -H "Content-Type: application/json" \
                  -d "{\\"roomId\\": \\"$WEBEX_ROOM_ID\\", \\"markdown\\": \\" Jenkins build failed for *cicd-webex* project.\\n\\n**Test Summary:**\\n${env.PYTEST_SUMMARY}\\"}" \
                  https://webexapis.com/v1/messages
                """
            }
        }

        always {
            echo "Build finished → WebEx notification attempted."
        }
    }
}
