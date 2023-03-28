pipeline{
    agent any
    
    stages{
        stage('SAST com Sonarqube'){
            environment {
                scanner = tool 'sonar-scanner'
            }
            steps{
                withSonarQubeEnv('sonarqube') {
                    sh "${scanner}/bin/sonar-scanner -Dsonar.projectKey=elasticcafe-app -Dsonar.sources=${WORKSPACE}/ -Dsonar.projectVersion=${BUILD_NUMBER}"
                }
                waitForQualityGate abortPipeline: true
            }
            
        }
        
    }

    post {
        success {
            echo "Pipeline executado com sucesso!!"
        }
        failure {
            echo "Pipeline falhou!"
        }
    }
}
