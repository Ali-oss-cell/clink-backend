# User List Endpoint Documentation

## Endpoint: `GET /api/users/`

This endpoint provides a paginated, filterable, and searchable list of users for the admin user management page.

## Features

✅ **Pagination** - Default 100 items per page, configurable via `page_size`  
✅ **Filtering** - By role, verification status, and active status  
✅ **Search** - By name or email  
✅ **Role-based Access Control** - Users only see what they're allowed to see  
✅ **Ordering** - Sortable by multiple fields  

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `role` | string | Filter by role | `?role=psychologist` |
| `search` | string | Search by name or email | `?search=john` |
| `is_verified` | boolean | Filter by verification status | `?is_verified=true` |
| `is_active` | boolean | Filter by active status | `?is_active=true` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page (default: 100) | `?page_size=50` |
| `ordering` | string | Sort field (prefix with `-` for descending) | `?ordering=-created_at` |

## Response Format

```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@clinic.com",
      "full_name": "Admin User",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "is_verified": true,
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "last_login": "2024-01-20T14:30:00Z",
      "phone_number": "+61400123456",
      "username": "admin"
    }
  ]
}
```

## User Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | number | ✅ Yes | User ID |
| `email` | string | ✅ Yes | User email |
| `full_name` | string | ✅ Yes | Full name (computed from first_name + last_name) |
| `first_name` | string | ❌ No | First name |
| `last_name` | string | ❌ No | Last name |
| `role` | string | ✅ Yes | One of: `admin`, `psychologist`, `practice_manager`, `patient` |
| `is_verified` | boolean | ✅ Yes | Email verification status |
| `is_active` | boolean | ✅ Yes | Account active status |
| `created_at` | string | ✅ Yes | ISO 8601 date string |
| `last_login` | string/null | ❌ No | ISO 8601 date string or null |
| `phone_number` | string | ❌ No | Phone number |
| `username` | string | ❌ No | Username |

## Example Requests

### Get all users
```bash
GET /api/users/
```

### Get only psychologists
```bash
GET /api/users/?role=psychologist
```

### Search for users
```bash
GET /api/users/?search=john
```

### Get verified users only
```bash
GET /api/users/?is_verified=true
```

### Get active admins
```bash
GET /api/users/?role=admin&is_active=true
```

### Pagination
```bash
GET /api/users/?page=2&page_size=50
```

### Combined filters
```bash
GET /api/users/?role=psychologist&is_verified=true&is_active=true&search=sarah&page=1&page_size=25
```

## Access Control

- **Admins & Practice Managers**: Can see all users
- **Psychologists**: Can see their patients and themselves
- **Patients**: Can only see themselves

## Implementation Details

- **Serializer**: `UserSerializer` - Includes all required fields with computed `full_name`
- **ViewSet**: `UserViewSet` - Uses `ModelViewSet` with custom filtering
- **Pagination**: `UserListPagination` - Default 100 items per page
- **Filtering**: DjangoFilterBackend for exact matches
- **Search**: SearchFilter for name/email search
- **Ordering**: OrderingFilter for sorting

## Frontend Integration

The endpoint is ready for use with the frontend user management page. It returns data in the exact format expected by the frontend, including:

- Pagination metadata (`count`, `next`, `previous`)
- User objects with all required fields
- Computed `full_name` field for display
- Proper date formatting (ISO 8601)

## Testing

Test the endpoint with:

```bash
# Get all users (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/api/users/

# Filter by role
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/api/users/?role=psychologist

# Search
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/api/users/?search=john
```

