pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME_FLASK = 'ganesh20101/flask-mysql-app:latest'
        DOCKER_IMAGE_NAME_MYSQL = 'ganesh20101/mysql:latest'
        MYSQL_DOCKERFILE_PATH = '/var/lib/jenkins/workspace/eks/mysql/Dockerfile'
        MYSQL_CONTEXT_PATH = '/var/lib/jenkins/workspace/eks/mysql/'
        K8S_NAMESPACE = 'default'  // Specify your Kubernetes namespace if it's different
        SERVICE_NAME = 'flask-service'  // LoadBalancer service name
    }

    stages {
        stage('Git Clone') {
            steps {
                script {
                    // Git clone from the main branch
                    git branch: 'main', url: 'https://github.com/ganesh20101/kubernetes.git'
                }
            }
        }

        stage('Terraform Init and Apply') {
            steps {
                script {
                    // Initialize Terraform and apply changes forcefully
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    // Docker build for Flask-MySQL app
                    sh "docker build -t $DOCKER_IMAGE_NAME_FLASK ."
                    // Docker build for MySQL image with specified Dockerfile and context
                    sh "docker build -f $MYSQL_DOCKERFILE_PATH -t $DOCKER_IMAGE_NAME_MYSQL $MYSQL_CONTEXT_PATH"
                }
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    // Docker push for Flask-MySQL app using credentials
                    withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        // Log in to Docker Hub with the credentials
                        sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"

                        // Docker push for Flask-MySQL app
                        sh "docker push $DOCKER_IMAGE_NAME_FLASK"

                        // Docker push for MySQL image
                        sh "docker push $DOCKER_IMAGE_NAME_MYSQL"
                    }
                }
            }
        }

        stage('Kubectl Apply') {
            steps {
                script {
                    // Kubectl apply commands for deployment
                    sh 'aws eks --region eu-north-1 update-kubeconfig --name my-eks-cluster'
                    sh 'kubectl apply -f flask-deployment.yaml'
                    sh 'kubectl apply -f service.yml'
                    sh 'kubectl apply -f sql.yml'
                    sh 'kubectl apply -f mysql-svc.yaml'
                }
            }
        }

        stage('Get Load Balancer DNS') {
            steps {
                script {
                    // Wait for the LoadBalancer to get an external IP or DNS
                    echo "Waiting for the LoadBalancer DNS to be available..."

                    // Fetch the DNS name of the LoadBalancer service
                    def lb_dns = sh(script: """
                        kubectl get svc $SERVICE_NAME -n $K8S_NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
                    """, returnStdout: true).trim()

                    // If DNS is not available yet, wait and try again
                    while (lb_dns == "") {
                        echo "DNS not available yet. Retrying..."
                        sleep(30)
                        lb_dns = sh(script: """
                            kubectl get svc $SERVICE_NAME -n $K8S_NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
                        """, returnStdout: true).trim()
                    }

                    echo "Load Balancer DNS: $lb_dns"
                }
            }
        }
    }

    post {
        always {
            // Clean up or post-processing if needed
            echo 'Pipeline completed'
        }
    }
}
