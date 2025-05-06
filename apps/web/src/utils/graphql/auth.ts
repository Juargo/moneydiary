import { gql } from "@urql/vue";

// Consulta para obtener información del usuario autenticado, incluyendo roles y permisos
export const ME_QUERY = gql`
  query Me {
    me {
      id
      email
      name
      profile_image
      is_active
      email_verified
      role {
        id
        name
        description
        permissions {
          id
          name
          resource
          action
          description
        }
      }
      permissions {
        id
        name
        resource
        action
        description
      }
    }
  }
`;

// Mutación para refrescar el token
export const REFRESH_TOKEN_MUTATION = gql`
  mutation RefreshToken($refreshToken: String!) {
    refreshToken(refreshToken: $refreshToken) {
      access_token
      refresh_token
      token_type
    }
  }
`;

// Mutación para cerrar sesión
export const LOGOUT_MUTATION = gql`
  mutation Logout {
    logout
  }
`;
