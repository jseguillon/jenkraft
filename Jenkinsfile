//PLEASE NOTE : you should create a token for api access  http://[your-jenkins]/user/[your-user]/configure
//PLEASE NOTE : first run will fail cause we need to approve static Math.random for groovy sandbox
//Go to : http://[your-jenkins]/scriptApproval/
//You should also consider increasing default number of executors http://[your-jenkins]/configure

import java.util.Random;

def randomFail() {
    randomNum = (int) (Math.random() * 20)
    //Force somtimes fail
    if (randomNum<1) {
        echo "Gonna fail"
        null.failnow()
    }
    else {
        echo "Go on !"
    }
    
    //Sleep for random time 
    randomNum = (int) (Math.random() * 60 + 60)
    echo "Let's sleep ${randomNum}"
    sleep randomNum
}

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                randomFail()
            }
        }
        stage('Anlyze') {
            steps {
                randomFail()
            }
        }
        stage('Test') {
            steps {
                randomFail()
            }
        }
        stage('Stage') {
            steps {
                randomFail()
            }
        }
        stage('Deploy') {
            steps {
                randomFail()
            }
        }
    }
}
