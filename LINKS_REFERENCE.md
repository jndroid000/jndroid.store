# 🔗 JN App Store - Complete Links Reference

**Last Updated:** February 11, 2026  
**Project:** jndroid.store  
**Base URL (Dev):** http://127.0.0.1:8000  
**Base URL (Prod):** https://jndroid.store

---

## 📍 **Core & Navigation URLs**

### Home & Public Pages
| Page | URL | Purpose |
|------|-----|---------|
| Home | `/` | Landing page |
| Support | `/support/` | Support/Help center |
| Community Guidelines | `/community-guidelines/` | Community rules |
| Report Bug | `/report-bug/` | Bug reporting form |
| Terms of Service | `/terms-of-service/` | Terms & conditions |
| Privacy Policy | `/privacy/` | Privacy policy |
| DMCA Takedown | `/dmca-takedown/` | DMCA takedown notice |

---

## 👤 **User & Account URLs**

| Feature | URL | Method | Requires Login |
|---------|-----|--------|---|
| Login | `/accounts/login/` | GET/POST | ❌ |
| Signup/Register | `/accounts/signup/` | GET/POST | ❌ |
| Logout | `/accounts/logout/` | GET/POST | ✅ |
| Email Verify | `/accounts/confirm-email/{key}/` | GET | ❌ |
| Email Resend | `/accounts/email/` | GET/POST | ✅ |
| Profile | `/accounts/profile/` | GET | ✅ |
| Change Password | `/accounts/password/change/` | GET/POST | ✅ |
| Reset Password | `/accounts/password/reset/` | GET/POST | ❌ |

---

## 📱 **Apps Management URLs**

### Browse Apps
| Feature | URL | Method | Purpose |
|---------|-----|--------|---------|
| All Apps | `/apps/` | GET | List all published apps |
| Search Apps | `/apps/?q=query` | GET | Search apps by title/description |
| Filter by Category | `/apps/?cat=android` | GET | Filter by category |
| App Details | `/apps/<slug>/` | GET | View single app details |
| App Download | `/apps/<slug>/download/` | GET | Track download & redirect |

### User's Apps Dashboard
| Feature | URL | Method | Requires Login |
|---------|-----|--------|---|
| My Apps Dashboard | `/apps/my-apps/` | GET | ✅ |
| Upload New App | `/apps/upload/` | GET/POST | ✅ |
| Edit App | `/apps/<slug>/edit/` | GET/POST | ✅ |
| Delete App | `/apps/<slug>/delete/` | GET/POST | ✅ |

---

## 🔗 **Link Management URLs**

### User DashBoard & Management
| Feature | URL | Method | Requires Login |
|---------|-----|--------|---|
| Links Dashboard | `/links/dashboard/` | GET | ✅ |
| Create Link | `/links/create/` | GET/POST | ✅ |
| Edit Link | `/links/<id>/edit/` | GET/POST | ✅ |
| Delete Link | `/links/<id>/delete/` | POST | ✅ |

### Public Links
| Feature | URL | Method | Public |
|---------|-----|--------|--------|
| Public Profile | `/links/@<username>/` | GET | ✅ |
| Track & Redirect | `/links/go/<id>/` | GET | ✅ |

---

## 📝 **Reviews & Ratings URLs**

| Feature | URL | Method | Purpose |
|---------|-----|--------|---------|
| App Reviews | `/reviews/<app_slug>/` | GET | View all reviews for app |
| Write Review | `/reviews/<app_slug>/create/` | GET/POST | Add review (requires login) |
| Edit Review | `/reviews/<review_id>/edit/` | GET/POST | Edit own review |
| Delete Review | `/reviews/<review_id>/delete/` | POST | Delete own review |

---

## 🏷️ **Categories URLs**

| Feature | URL | Method | Purpose |
|---------|-----|--------|---------|
| All Categories | `/categories/` | GET | List all categories |
| Category Details | `/categories/<slug>/` | GET | Apps in category |

---

## 🛠️ **Admin & Management URLs**

### Django Admin Panel
| Feature | URL | Method | Requires |
|---------|-----|--------|----------|
| Admin Dashboard | `/admin/` | GET/POST | Staff/Superuser |
| Users Management | `/admin/auth/user/` | GET/POST | Staff |
| Apps Management | `/admin/apps/app/` | GET/POST | Staff |
| Links Management | `/admin/links/link/` | GET/POST | Staff |
| Reviews Management | `/admin/reviews/review/` | GET/POST | Staff |
| Categories Management | `/admin/categories/category/` | GET/POST | Staff |

### Custom Admin Panel
| Feature | URL | Method | Requires |
|---------|-----|--------|----------|
| Dashboard | `/admin-panel/` | GET | Staff |

---

## 🔐 **Authentication & AllAuth URLs**

| Feature | URL | Purpose |
|---------|-----|---------|
| Login | `/accounts/login/` | User login |
| Logout | `/accounts/logout/` | User logout |
| Signup | `/accounts/signup/` | New user registration |
| Email Confirmation | `/accounts/confirm-email/` | Verify email address |
| Password Reset | `/accounts/password/reset/` | Forgot password |
| Password Change | `/accounts/password/change/` | Change password (logged in) |

---

## 📊 **API Endpoints** (Future)

```
/api/v1/apps/                    # List/Create apps
/api/v1/apps/<id>/               # Get/Update/Delete app
/api/v1/apps/<id>/download/      # Track download
/api/v1/reviews/                 # Reviews API
/api/v1/links/                   # Links API
/api/v1/categories/              # Categories API
/api/v1/users/<username>/        # User profile API
```

---

## 🌐 **External Resources**

| Resource | URL | Purpose |
|----------|-----|---------|
| GitHub Repository | https://github.com/jndroid000/jndroid.store | Source code |
| Documentation | `/docs/` | API docs |
| Status Page | `/status/` | Service status |
| Support Email | support@jndroid.store | Customer support |

---

## 📱 **URL Patterns Summary**

### Main App Routes (config/urls.py)
```
'' → core.home
'admin/' → Django admin
'accounts/' → User auth
'apps/' → Apps management
'links/' → Link management
'reviews/' → Reviews
'categories/' → Categories
'admin-panel/' → Custom admin
```

### Nested Routes

**Apps URLs (apps/urls.py)**
```
/apps/
├── '' → list all apps
├── 'upload/' → create app
├── 'my-apps/' → user dashboard
├── '<slug>/' → app details
├── '<slug>/edit/' → edit app
├── '<slug>/delete/' → delete app
└── '<slug>/download/' → track download
```

**Links URLs (links/urls.py)**
```
/links/
├── 'dashboard/' → user dashboard
├── 'create/' → create link
├── '<id>/edit/' → edit link
├── '<id>/delete/' → delete link
├── '@<username>/' → public profile
└── 'go/<id>/' → track & redirect
```

---

## 🔍 **URL Naming Convention**

All URLs follow Django's `url name` pattern for easy reference in templates:

```django
<!-- Login page -->
{% url 'accounts:login' %}

<!-- App detail -->
{% url 'apps:detail' app.slug %}

<!-- My apps dashboard -->
{% url 'apps:my_apps' %}

<!-- Links dashboard -->
{% url 'links:dashboard' %}

<!-- Public profile -->
{% url 'links:public_profile' username %}
```

---

## 📝 **Quick Reference - Form Submission URLs**

| Form | Submits To | Method |
|------|----------|--------|
| App Upload | `/apps/upload/` | POST |
| App Edit | `/apps/<slug>/edit/` | POST |
| App Delete | `/apps/<slug>/delete/` | POST |
| Create Link | `/links/create/` | POST |
| Edit Link | `/links/<id>/edit/` | POST |
| Delete Link | `/links/<id>/delete/` | POST |
| Review Submit | `/reviews/<app_slug>/create/` | POST |
| User Login | `/accounts/login/` | POST |
| User Register | `/accounts/signup/` | POST |

---

## 🚀 **Development vs Production**

### Development
```
Base: http://127.0.0.1:8000
Admin: http://127.0.0.1:8000/admin/
Debug: True
```

### Production
```
Base: https://jndroid.store
Admin: https://jndroid.store/admin/
Debug: False
SSL: Enabled
```

---

## 📌 **Important Notes**

- ✅ All URLs require proper CSRF token for POST requests
- ✅ Login-required views redirect to `/accounts/login/`
- ✅ Staff-only views require `is_staff=True`
- ✅ 404 errors on non-existent resources
- ✅ Pagination implemented on list views (default: 20 items/page)

---

**Created:** February 11, 2026  
**Last Updated:** February 11, 2026  
**Version:** 1.0

---

*Keep this file updated whenever new URLs are added to the project!* 📝
