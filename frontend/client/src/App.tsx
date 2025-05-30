import React, { useEffect, useState } from 'react'
import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  useQuery,
  useSubscription,
  gql,
  split,
  HttpLink,
} from '@apollo/client'
import { GraphQLWsLink } from '@apollo/client/link/subscriptions'
import { createClient } from 'graphql-ws'
import { getMainDefinition } from '@apollo/client/utilities'

interface User {
  id: string
  username: string
  status: number
}

const USERS_QUERY = gql`
  query GetUsers {
    users {
      id
      username
      status
    }
  }
`

const USER_CHANGED_SUBSCRIPTION = gql`
  subscription OnUserChanged {
    userChanged {
      id
      username
      status
    }
  }
`

const httpLink = new HttpLink({ uri: 'http://localhost:4000/graphql' })

const wsLink = new GraphQLWsLink(
  createClient({
    url: 'ws://localhost:4000/graphql',
  }),
)

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query)
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    )
  },
  wsLink,
  httpLink,
)

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
})

const Users: React.FC = () => {
  const { data, loading } = useQuery<{ users: User[] }>(USERS_QUERY)
  const { data: subData } = useSubscription<{ userChanged: User }>(
    USER_CHANGED_SUBSCRIPTION,
  )
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    if (data) setUsers(data.users)
  }, [data])

  useEffect(() => {
    if (subData?.userChanged) {
      console.log(
        'User changed: ' +
          subData.userChanged.id +
          ', status=' +
          subData.userChanged.status,
      )
      setUsers((prev) => [...prev])
    }
  }, [subData])

  if (loading) return <p>Loading...</p>

  return (
    <ul>
      {users.map((user) => (
        <li id={'user-' + user.id} key={user.id}>
          {user.username}: status={user.status}
        </li>
      ))}
    </ul>
  )
}

const App: React.FC = () => (
  <ApolloProvider client={client}>
    <h1>Users</h1>
    <Users />
  </ApolloProvider>
)

export default App
