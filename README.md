1. API Gateway
   ```bash
   docker build -t lilarin/api-gateway:latest -f ./microservices/api_gateway/Dockerfile ./microservices
   docker push lilarin/api-gateway:latest
2. Tags Service
   ```bash
   docker build -t lilarin/tags-service:latest -f ./microservices/tags_service/Dockerfile ./microservices
   docker push lilarin/tags-service:latest
3. Collections Service
   ```bash
   docker build -t lilarin/collections-service:latest -f ./microservices/collections_service/Dockerfile ./microservices
   docker push lilarin/collections-service:latest
4. Filter Service
   ```bash
   docker build -t lilarin/filter-service:latest -f ./microservices/filter_service/Dockerfile ./microservices
   docker push lilarin/filter-service:latest
5. Router Service
   ```bash
   docker build -t lilarin/router-service:latest -f ./microservices/router_service/Dockerfile ./microservices
   docker push lilarin/router-service:latest
6. Shard Service
   ```bash
   docker build -t lilarin/shard-service:latest -f ./microservices/shard_service/Dockerfile ./microservices
   docker push lilarin/shard-service:latest
7. AI Service 
   ```bash
   docker build -t lilarin/ai-service:latest -f ./microservices/ai_service/Dockerfile ./microservices
   docker push lilarin/ai-service:latest
8. MCP Server 
   ```bash
   docker build -t lilarin/mcp-server:latest -f ./microservices/mcp_server/Dockerfile .
   docker push lilarin/mcp-server:latest
