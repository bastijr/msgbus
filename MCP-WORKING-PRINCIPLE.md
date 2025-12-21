# MCP (Model Context Protocol) Working Principle

## Overview

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between Large Language Model (LLM) applications and external data sources and tools. MCP provides a standardized way for AI assistants to securely access various resources and capabilities.

## Core Architecture

### 1. Client-Server Architecture

MCP follows a client-server architecture pattern:

- **MCP Client (Host)**: Runs in the LLM application, responsible for initiating connections and requests
- **MCP Server**: Provides specific context, tools, and resource access capabilities
- **Transport Layer**: Handles communication between client and server

```
┌─────────────────┐         ┌──────────────────┐
│  LLM Application │◄───────►│   MCP Server     │
│   (MCP Client)   │         │ (Resources/Tools)│
└─────────────────┘         └──────────────────┘
         │                           │
         └─────── MCP Protocol ──────┘
```

### 2. Three Core Components

#### Resources
- Provide contextual data to the LLM
- Can be file contents, database records, API responses, etc.
- Servers expose resources through URI schemes
- Clients can read and subscribe to resource updates

#### Prompts
- Pre-defined prompt templates
- Can include parameterized context
- Help users quickly utilize common workflows
- Servers can provide multiple reusable prompts

#### Tools
- Functions that the LLM can invoke
- Allow AI to perform actions and retrieve information
- Servers define tool schemas and implementations
- Clients proxy LLM calls to these tools

## Workflow

### Connection Establishment

1. **Initialize**: Client starts and connects to MCP server
2. **Capability Negotiation**: Both parties exchange supported features and protocol versions
3. **Authentication**: Perform identity verification if required
4. **Ready**: Connection established, ready for interaction

### Typical Interaction Flow

```
User → LLM App → MCP Client → MCP Server → External Resources
                     ↓
                Get Response
                     ↓
    ← Process Result ← Return Data ←
```

#### Example: File Reading Scenario

1. User requests: "Read the config.json file"
2. LLM recognizes the need to access filesystem
3. MCP client requests resource from filesystem MCP server
4. Server reads file and returns content
5. Client provides content to LLM
6. LLM processes content and responds to user

## Protocol Features

### 1. Standardized Message Format

MCP uses JSON-RPC 2.0 as the message format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "file:///path/to/file.txt"
  }
}
```

### 2. Transport Layer Abstraction

Supports multiple transport methods:
- **stdio**: Communication through standard input/output
- **HTTP/SSE**: HTTP-based Server-Sent Events
- **WebSocket**: Bidirectional real-time communication

### 3. Security Mechanisms

- **Permission Control**: Servers can restrict access to specific resources
- **Sandbox Isolation**: Tool execution in controlled environments
- **Audit Logging**: Record all operations for review

## Core Concepts

### Server Capabilities

Servers declare their capabilities during initialization:

```json
{
  "capabilities": {
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "tools": {
      "listChanged": true
    },
    "prompts": {
      "listChanged": true
    }
  }
}
```

### Sampling

- Allows servers to request LLM inference
- Servers can invoke LLM during tool execution
- Enables more complex AI agent workflows

### Progress Notifications

- Long-running operations can report progress
- Uses standardized progress notification format
- Improves user experience and transparency

## Practical Use Cases

### 1. Filesystem Integration
- Read and write local files
- Search file contents
- Monitor file changes

### 2. Database Access
- Query databases
- Perform CRUD operations
- Retrieve schema information

### 3. API Integration
- Call external REST APIs
- Access web services
- Retrieve real-time data

### 4. Development Tools
- Git operations
- Code analysis
- Test execution

### 5. Enterprise Systems
- CRM integration
- Project management tools
- Internal knowledge base access

## Advantages

1. **Standardization**: Unified protocol reduces integration complexity
2. **Extensibility**: Easily add new data sources and tools
3. **Security**: Built-in permission control and isolation mechanisms
4. **Flexibility**: Supports multiple transport methods and deployment modes
5. **Interoperability**: Different implementations can communicate with each other

## Relationship to Message Bus

While MCP and traditional message buses (like the msgbus project) solve different problems, they share some similarities:

- **Communication Abstraction**: Both provide an abstraction layer for inter-component communication
- **Protocol Standardization**: Define standardized message formats and interaction patterns
- **Decoupling**: Achieve loose coupling between components
- **Extensibility**: Support adding new services and capabilities

Key Differences:
- **MCP**: Specifically designed for LLM-tool integration, focuses on context provision
- **Message Bus**: General-purpose inter-process communication framework, focuses on high-throughput message delivery

## Summary

MCP provides a powerful and flexible framework that enables LLM applications to securely access external resources and tools. Through standardized protocols and clear architecture, MCP simplifies AI application development, allowing seamless integration with various data sources and systems.

Whether building personal AI assistants or enterprise-level AI applications, understanding MCP's working principle is key to fully leveraging its capabilities.
