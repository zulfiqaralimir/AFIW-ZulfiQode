"""
Neo4j Integration
Stores and retrieves Lawyer-AI analysis results in Neo4j graph database
"""
from neo4j import GraphDatabase
from typing import Dict, Optional, List, Any
from app.core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# 🕸 Neo4j Integration
# ---------------------------------------------------------
class Neo4jClient:
    """
    Neo4j Client for storing and retrieving Lawyer-AI analysis results
    """
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initialize Neo4j client
        
        Args:
            uri: Neo4j connection URI (default: bolt://localhost:7687)
            user: Neo4j username (default: neo4j)
            password: Neo4j password (default: password)
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("✅ Connected to Neo4j successfully.")
        except Exception as e:
            logger.warning(f"Neo4j driver not installed or connection failed: {e}")
            self.driver = None
    
    def close(self):
        """Close Neo4j driver connection"""
        if self.driver:
            self.driver.close()
    
    def store_company_analysis(self, data: dict):
        """
        Creates/updates a Company node with Lawyer-AI analysis attributes.
        
        Args:
            data: Complete Lawyer-AI analysis result dictionary
        """
        if not self.driver:
            return
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Company {name: $name})
                SET c.tone = $tone,
                    c.ethics = $ethics,
                    c.risk = $risk,
                    c.CII = $CII,
                    c.TIT = $TIT,
                    c.OCF = $OCF,
                    c.GME = $GME,
                    c.FPP = $FPP,
                    c.HS = $HS,
                    c.LastUpdated = datetime()
                RETURN c.name AS name
                """
                
                session.run(query, {
                    "name": data["company_name"],
                    "tone": data["tone"],
                    "ethics": data["ethical_flag"],
                    "risk": data["risk_level"],
                    "CII": data["composite_integrity_index"]["cii_score"],
                    "TIT": data["temporal_integrity_trend"]["tit_value"],
                    "OCF": data["operational_metrics"]["operational_cash_flow"]["ocf_value"],
                    "GME": data["operational_metrics"]["gross_margin_effect"]["gross_margin_percent"],
                    "FPP": data["future_performance_perspective"]["outlook"],
                    "HS": data["hallucination_metrics"]["hallucination_score"]
                })
                logger.info(f"🕸 Neo4j node updated for {data['company_name']}")
        except Exception as e:
            logger.error(f"Neo4j insert failed: {e}")


# Backward compatibility
class Neo4jIntegration:
    """
    Neo4j Integration class (backward compatibility wrapper)
    """
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j integration
        
        Args:
            uri: Neo4j connection URI (default: from settings)
            user: Neo4j username (default: from settings)
            password: Neo4j password (default: from settings)
        """
        from app.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {str(e)}")
            self.driver = None
    
    def close(self):
        """Close Neo4j driver connection"""
        if self.driver:
            self.driver.close()
    
    def store_company_analysis(
        self,
        company_name: str,
        analysis: Dict,
        analysis_id: Optional[str] = None
    ) -> Dict:
        """
        Store company analysis in Neo4j (backward compatibility).
        
        Args:
            company_name: Company name
            analysis: Analysis result dictionary
            analysis_id: Optional analysis ID
            
        Returns:
            Dictionary with node information
        """
        if not self.driver:
            return {"node_id": None, "error": "Neo4j driver not available"}
        
        try:
            # Prepare data for Neo4jClient
            data = {
                "company_name": company_name,
                "tone": analysis.get("tone", "neutral"),
                "ethical_flag": analysis.get("ethical_flag", "questionable"),
                "risk_level": analysis.get("risk_level", "moderate"),
                "composite_integrity_index": analysis.get("composite_integrity_index", {}),
                "temporal_integrity_trend": analysis.get("temporal_integrity_trend", {}),
                "operational_metrics": analysis.get("operational_metrics", {}),
                "future_performance_perspective": analysis.get("future_performance_perspective", {}),
                "hallucination_metrics": analysis.get("hallucination_metrics", {})
            }
            
            # Use Neo4jClient to store
            client = Neo4jClient(self.uri, self.user, self.password)
            client.store_company_analysis(data)
            client.close()
            
            return {"node_id": company_name, "status": "success"}
            
        except Exception as e:
            logger.error(f"Failed to store company analysis in Neo4j: {str(e)}", exc_info=True)
            return {"node_id": None, "error": str(e)}
    
    def create_analysis_relationship(
        self,
        company_name: str,
        analysis_id: str
    ) -> bool:
        """
        Create relationship between Company and Analysis (backward compatibility).
        
        Args:
            company_name: Company name
            analysis_id: Analysis ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Company {name: $company_name})
                MERGE (a:Analysis {id: $analysis_id})
                MERGE (c)-[:HAS_ANALYSIS]->(a)
                RETURN c.name, a.id
                """
                
                result = session.run(query, {
                    "company_name": company_name,
                    "analysis_id": analysis_id
                })
                
                if result.single():
                    logger.info(f"Created relationship between {company_name} and analysis {analysis_id}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to create analysis relationship: {str(e)}", exc_info=True)
            return False
    
    def get_company(self, company_name: str) -> Optional[Dict]:
        """
        Get company node from Neo4j (backward compatibility).
        
        Args:
            company_name: Company name
            
        Returns:
            Company node data or None
        """
        if not self.driver:
            return None
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Company {name: $name})
                RETURN c
                """
                
                result = session.run(query, {"name": company_name})
                record = result.single()
                
                if record:
                    node = record["c"]
                    return dict(node)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get company from Neo4j: {str(e)}", exc_info=True)
            return None
    
    def get_all_companies(self) -> List[Dict]:
        """
        Get all company nodes from Neo4j (backward compatibility).
        
        Returns:
            List of company node data
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Company)
                RETURN c
                """
                
                result = session.run(query)
                companies = []
                
                for record in result:
                    node = record["c"]
                    companies.append(dict(node))
                
                return companies
                
        except Exception as e:
            logger.error(f"Failed to get companies from Neo4j: {str(e)}", exc_info=True)
            return []
    
    def generate_cypher_query(self, query_type: str, **kwargs) -> str:
        """
        Generate Cypher query (backward compatibility).
        
        Args:
            query_type: Type of query to generate
            **kwargs: Additional parameters
            
        Returns:
            Cypher query string
        """
        if query_type == "get_company":
            company_name = kwargs.get("company_name", "")
            return f"MATCH (c:Company {{name: '{company_name}'}}) RETURN c"
        
        elif query_type == "get_all_companies":
            return "MATCH (c:Company) RETURN c"
        
        elif query_type == "get_company_analyses":
            company_name = kwargs.get("company_name", "")
            return f"MATCH (c:Company {{name: '{company_name}'}})-[:HAS_ANALYSIS]->(a:Analysis) RETURN a"
        
        else:
            return "MATCH (n) RETURN n LIMIT 10"
