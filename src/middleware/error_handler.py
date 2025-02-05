from fastapi import Request, HTTPException, status, Response
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint



class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and errors.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """
        Dispatches the request and handles any exceptions.

        Args:
            request (Request): The incoming request.
            call_next (RequestResponseEndpoint): The next endpoint to call.

        Returns:
            Response: The response from the next endpoint.
        """
        try:
          response = await call_next(request)
          return response
        except Exception as exc:
            # Generic error handling for all exceptions
            print(f"Unhandled exception: {exc}")  # Log the exception
            # Return a user-friendly error page
            error_html = "<html><body><h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p></body></html>"
            return HTMLResponse(content=error_html, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

