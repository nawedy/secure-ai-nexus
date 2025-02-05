# SecureAI API Documentation



This is the documentation for the SecureAI API.

## Introduction

This document provides comprehensive information about the SecureAI API, enabling developers to integrate their applications with our secure AI platform. SecureAI offers a robust set of features, including secure user authentication, password management, and access to advanced AI models. All interactions with the API are designed with security and privacy in mind.

## Authentication

SecureAI uses JSON Web Tokens (JWT) for authentication. To access most of the API endpoints, you will need to include a valid JWT in the `Authorization` header of your requests.

### Obtaining a JWT

1.  **User Login:** Send a POST request to the `/auth/login` endpoint with valid user credentials (email and password).
2.  **Response:** If successful, the server will return a JWT in the response body:
```
json
    {
      "access_token": "your_jwt_here",
      "token_type": "bearer"
    }
    
```
### Including the JWT in Requests

Include the JWT in the `Authorization` header of your requests as a `Bearer` token:
```
Authorization: Bearer your_jwt_here
```
### Token Expiration and Renewal

JWTs have an expiration time. You will need to obtain a new token by logging in again once it expires.

### MFA (Multi-Factor Authentication)

Multi-factor authentication (MFA) is **mandatory** during account creation/registration. Users must choose at least one of the following methods for 2FA:

*   Text messaging
*   Email
*   Authentication apps

When the user register, he will be asked to enter a code.

### Account recovery code
The user can generate a recovery code to be able to access the account.
You can only use one time this code.
## Security Measures

SecureAI prioritizes the security and privacy of user data. Here are some of the security measures implemented:

*   **Encryption in Transit:** All communications are encrypted using HTTPS/TLS.
*   **Encryption at Rest:** Sensitive data, like passwords, are stored in an encrypted format.
*   **Password Complexity:** Strong password requirements are enforced, including minimum length and special character checks.
*   **Token Revocation:** Users can log out and revoke their access tokens.
*   **Role-Based Access Control (RBAC):** User roles and permissions are strictly enforced.
*   **Data Sanitization:** All user inputs are sanitized to prevent security vulnerabilities.
*   **Data Validation:** Strict input validation rules are enforced.
* **Token reset**: limit the number of tries for the token reset.
* **MFA**: MFA is mandatory.
* **Recovery code**: Account recovery code is available.

## Endpoints
All the endpoint need to have the `Authorization: Bearer <your_token>` header.

### /auth/register

*   **Method:** POST
*   **Description:** User registration.
*   **Request Body:**
    

### /auth/login

*   **Method:** POST
*   **Description:** User login.
* **Placeholder: Request**
* **Placeholder: Response**

### /auth/logout

*   **Method:** POST
*   **Description:** User logout.
* **Placeholder: Request**
* **Placeholder: Response**

### /auth/password-reset

*   **Method:** POST
*   **Description:** Initiate password reset.
* **Placeholder: Request**
* **Placeholder: Response**

### /auth/reset-password

*   **Method:** POST
*   **Description:** Confirm password reset.
* **Placeholder: Request**
* **Placeholder: Response**

### Model Access Endpoints

*   **Description:** These endpoints allow authenticated users to interact with the LLMs and Gen AI models.

### /models/generate

* **Method**: POST
* **Description**: generate text.
* **Placeholder: Request**
* **Placeholder: Response**

### /models/list

* **Method**: GET
* **Description**: List the available models.
* **Placeholder: Request**
* **Placeholder: Response**

## Data Formats

*   **Description:** This section will detail the JSON schemas for the various data structures used in requests and responses.

*   **Placeholder:** Data formats will be defined here.