import sys
import os
import logging
from typing import List

import dotenv
from embedchain import App

from flask import Flask
from theoriq import AgentConfig, ExecuteContext, ExecuteResponse
from theoriq.biscuit import TheoriqCost
from theoriq.extra.flask import theoriq_blueprint
from theoriq.schemas import ExecuteRequestBody, TextItemBlock
from theoriq.types import Currency
dotenv.load_dotenv()


# Configure logging to both file and console
def setup_logging():
    """Configure logging to output to both file and console"""
    # Create formatters for our logs
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create and configure file handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Get the root logger and add both handlers
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

class Config:
    """Configuration management class"""
    def __init__(self):
        self.WEB_SOURCES_PATH = "url.txt"
        self.PDF_PATH = "litepaper.pdf"
        self.JSON_PATH = "img_data.json"  # Added based on original code's usage
        self.CONFIG_PATH = "config.yaml"

    def load_web_sources(self) -> List[str]:
        """Load web sources from file"""
        try:
            with open(self.WEB_SOURCES_PATH, "r") as file:
                return [line.strip() for line in file]
        except Exception as e:
            logger.error(f"Failed to load web sources: {e}")
            return []

class RAGAgent:
    """
    A Retrieval-Augmented Generation (RAG) agent using Embedchain
    """
    def __init__(self, config: Config):
        """
        Initialize the RAG agent with configuration
        
        :param config: Config instance containing paths and settings
        """
        self.config = config
        try:
            # Ensure db directory exists and is empty
            db_path = "db"
            if os.path.exists(db_path):
                if not os.path.isdir(db_path):
                    raise RuntimeError(f"{db_path} exists but is not a directory")
                # Optional: Clean existing db on startup
                # shutil.rmtree(db_path)
                # os.makedirs(db_path)
            else:
                os.makedirs(db_path)
            self.app = App.from_config(config_path=config.CONFIG_PATH)
            self._initialize_sources()
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent: {e}")
            raise

    def _initialize_sources(self):
        """Initialize all data sources"""
        # Add web sources
        web_sources = self.config.load_web_sources()
        for source in web_sources:
            try:
                self.app.add(source, data_type='web_page')
                # logger.info(f"Added web source: {source}")
            except Exception as e:
                logger.error(f"Failed to add web source {source}: {e}")

        # Add PDF source
        try:
            self.app.add(self.config.PDF_PATH, data_type='pdf_file')
            logger.info(f"Added PDF source: {self.config.PDF_PATH}")
        except Exception as e:
            logger.error(f"Failed to add PDF source {self.config.PDF_PATH}: {e}")
            
        # Add JSON source
        try:
            self.app.add(self.config.JSON_PATH)
            logger.info(f"Added JSON source: {self.config.JSON_PATH}")
        except Exception as e:
            logger.error(f"Failed to add JSON source {self.config.JSON_PATH}: {e}")

    def chat(self, query: str) -> str:
        """
        Query the RAG system
        
        :param query: User's query
        :return: Generated response
        """
        try:
            response = self.app.chat(query)
            return response
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return "I apologize, but I couldn't process your query."
        
class TheoriqHandler:
    """Handles Theoriq-specific operations and response formatting."""
    
    @staticmethod
    def create_response(
        context: ExecuteContext,
        text: str,
        cost: float = 1.0,
        currency: Currency = Currency.USDC
    ) -> ExecuteResponse:
        """Create a formatted Theoriq response."""
        return context.new_response(
            blocks=[TextItemBlock(text=text)],
            cost=TheoriqCost(amount=cost, currency=currency),
        )


class TheoriqServer:
    """Theoriq server implementation"""
    def __init__(self):
        self.config = Config()
        self.rag_agent = RAGAgent(self.config)

    def execute(self, context: ExecuteContext, req: ExecuteRequestBody) -> ExecuteResponse:
        """
        Execute method for Theoriq agent
        
        :param context: Execution context
        :param req: Request body
        :return: Execution response
        """
        
        try:
            # Extract and validate user input
            if not req.last_item or not req.last_item.blocks:
                raise ValueError("Invalid request: No input blocks found")
            text_value = req.last_item.blocks[0].data.text.strip()
            
            if not text_value:
                raise ValueError("Invalid request: Empty input")
            logger.info(f"Received query: {text_value}")

            # Query RAG agent
            response_text = self.rag_agent.chat(text_value)
            logger.info(f"Generated response: {response_text}")

            # Create Theoriq response           
            execute_response = TheoriqHandler.create_response(context, response_text)
            
            # Log the cost of the request
            logger.info(f"Request {context.request_id} cost: {execute_response.theoriq_cost.amount} {execute_response.theoriq_cost.currency}")
            
            return execute_response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            error_response = "I apologize, but an error occurred while processing your request. Please try again."
            return TheoriqHandler.create_response(context, error_response)
    
    

    def create_app(self):
        """
        Create a Flask app with a single route to handle Theoriq protocol requests.
        """
        app = Flask(__name__)
        app.config['DEBUG'] = True

        agent_config = AgentConfig.from_env()
        blueprint = theoriq_blueprint(agent_config, self.execute)
        app.register_blueprint(blueprint)

        return app