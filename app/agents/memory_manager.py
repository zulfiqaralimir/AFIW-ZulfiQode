"""
Handles Temporal Analytical Memory (TAM) persistence.
"""
from datetime import datetime
from app.data.neo4j_integration import Neo4jClient
from app.core.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Manages Temporal Analytical Memory (TAM) for storing historical analysis snapshots.
    """
    
    def __init__(self):
        self.neo4j = Neo4jClient()
    
    def store_snapshot(self, company, cii, tit, ethics, risk, source="Lawyer-AI v9.0"):
        """
        Store a temporal snapshot of analysis results in Neo4j.
        
        Args:
            company: Company name
            cii: Composite Integrity Index score
            tit: Temporal Integrity Trend value
            ethics: Ethical flag
            risk: Risk level
            source: Source of analysis
        """
        if not self.neo4j.driver:
            logger.warning("Neo4j not available, skipping memory snapshot")
            return
        
        try:
            query = """
            MERGE (c:Company {name:$company})
            MERGE (m:Memory {company:$company, timestamp:$timestamp})
            SET m.cii=$cii, m.tit=$tit, m.ethics=$ethics, m.risk=$risk, m.source=$source
            MERGE (c)-[:HAS_MEMORY]->(m)
            RETURN m
            """
            
            with self.neo4j.driver.session() as session:
                result = session.run(query, {
                    "company": company,
                    "timestamp": datetime.utcnow().isoformat(),
                    "cii": cii,
                    "tit": tit,
                    "ethics": ethics,
                    "risk": risk,
                    "source": source
                })
                record = result.single()
                if record:
                    logger.info(f"✅ Memory snapshot stored for {company}")
                    return dict(record["m"]) if record["m"] else None
        except Exception as e:
            logger.error(f"Failed to store memory snapshot: {e}")
            return None
    
    def retrieve_last_snapshot(self, company):
        """
        Retrieve the last analysis snapshot for a company.
        
        Args:
            company: Company name
            
        Returns:
            Last memory snapshot or None
        """
        if not self.neo4j.driver:
            return None
        
        try:
            query = """
            MATCH (c:Company {name:$company})-[:HAS_MEMORY]->(m:Memory)
            RETURN m
            ORDER BY m.timestamp DESC
            LIMIT 1
            """
            
            with self.neo4j.driver.session() as session:
                result = session.run(query, {"company": company})
                record = result.single()
                if record:
                    return dict(record["m"])
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve memory snapshot: {e}")
            return None
    
    def retrieve_all_snapshots(self, company):
        """
        Retrieve all analysis snapshots for a company.
        
        Args:
            company: Company name
            
        Returns:
            List of memory snapshots
        """
        if not self.neo4j.driver:
            return []
        
        try:
            query = """
            MATCH (c:Company {name:$company})-[:HAS_MEMORY]->(m:Memory)
            RETURN m
            ORDER BY m.timestamp DESC
            """
            
            with self.neo4j.driver.session() as session:
                result = session.run(query, {"company": company})
                snapshots = []
                for record in result:
                    snapshots.append(dict(record["m"]))
                return snapshots
        except Exception as e:
            logger.error(f"Failed to retrieve memory snapshots: {e}")
            return []

