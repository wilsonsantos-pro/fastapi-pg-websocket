import { ApolloServer } from '@apollo/server'
import { expressMiddleware } from '@apollo/server/express4'
import { makeExecutableSchema } from '@graphql-tools/schema'
import express from 'express'
import http from 'http'
import cors from 'cors'
import bodyParser from 'body-parser'
import { WebSocketServer } from 'ws'
import { useServer } from 'graphql-ws/lib/use/ws'
import { PubSub } from 'graphql-subscriptions'
import fetch from 'node-fetch'
import WebSocket from 'ws'
import path from 'path'
import { fileURLToPath } from 'url'

interface User {
  id: number
  username: string
  status: number
}

const pubsub = new PubSub()
const USER_CHANGED = 'USER_CHANGED'

const typeDefs = `#graphql
  type User {
    id: ID!
    username: String!
    status: Int!
  }

  type Query {
    users: [User!]!
  }

  type Subscription {
    userChanged: User!
  }
`

const resolvers = {
  Query: {
    users: async (): Promise<User[]> => {
      console.log('🔍 Resolving users query...')
      try {
        const res = await fetch('http://rest:8000/users')
        const data = (await res.json()) as {
          id: number
          username: string
          status: number
        }[]
        console.log(`✅ Fetched ${data.length} users`)
        return data.map((u) => ({
          id: u.id,
          username: u.username,
          status: u.status,
        }))
      } catch (err) {
        console.error('❌ Failed to fetch users:', err)
        return []
      }
    },
  },
  Subscription: {
    userChanged: {
      subscribe: () => pubsub.asyncIterableIterator([USER_CHANGED]),
    },
  },
}

const schema = makeExecutableSchema({ typeDefs, resolvers })

const app = express()
const httpServer = http.createServer(app)

const wsServer = new WebSocketServer({ server: httpServer, path: '/graphql' })
useServer({ schema }, wsServer)

const server = new ApolloServer({ schema })
await server.start()

app.use('/graphql', cors(), bodyParser.json(), expressMiddleware(server))

httpServer.listen(4000, () => {
  console.log('Server running at http://localhost:4000/graphql')
})

function connectWithRetry() {
  const backendWs = new WebSocket('ws://rest:8000/ws/users')

  backendWs.on('open', () => {
    console.log('✅ Connected to backend WebSocket')
  })

  backendWs.on('message', (data: WebSocket.RawData) => {
    try {
      const user = JSON.parse(data.toString()) as User
      console.log(`✅ User notification ${user.id}, status=${user.status}`)
      if (user?.id && user?.username) {
        pubsub.publish(USER_CHANGED, { userChanged: user })
        console.log(`✅ User published ${user.id}`)
      }
    } catch (err) {
      console.error('❌ Failed to parse WebSocket message:', err)
    }
  })

  backendWs.on('close', () => {
    console.warn('⚠️ WebSocket closed. Reconnecting in 3s...')
    setTimeout(connectWithRetry, 3000)
  })

  backendWs.on('error', (err) => {
    console.error('❌ WebSocket error:', err.message)
    backendWs.close() // Force close to trigger retry
  })
}

connectWithRetry()

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Serve static React files
app.use(express.static(path.join(__dirname, 'public')))

// Fallback for React Router
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'))
})
