# Azure DevOps CI/CD Pipeline for LLM Chatbot

trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Build
  displayName: 'Build Stage'
  jobs:
  - job: Build
    steps:
    - task: UseNode@2
      inputs:
        version: '16.x'
    - script: |
        cd frontend
        npm install
        npm run build
      displayName: 'Install and Build Frontend'
    - script: |
        cd backend
        pip install -r requirements.txt
      displayName: 'Install Backend Dependencies'
    - task: CopyFiles@2
      inputs:
        sourceFolder: '$(Build.SourcesDirectory)'
        targetFolder: '$(Build.ArtifactStagingDirectory)'
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: '$(Build.ArtifactStagingDirectory)'
        artifactName: 'drop'

- stage: Deploy
  displayName: 'Deploy Stage'
  jobs:
  - job: Deploy
    steps:
    - task: AzureWebApp@1
      inputs:
        azureSubscription: 'Your-Azure-Subscription'
        appName: 'your-webapp-name'
        package: '$(Build.ArtifactStagingDirectory)/drop'
