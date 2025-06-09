
# UPC Product Review System

A comprehensive Django-based web application for managing UPC product submissions with role-based approval workflows.

## Features

### 🎯 Core Functionality
- **Role-based Authentication**: Admin, Manager, and Team Member roles
- **Product Submission**: UPC/EAN code entry with detailed product information
- **Review Workflow**: Approval/rejection system with notification alerts
- **Dynamic Attributes**: Custom key-value pairs for additional product information
- **Edit Logging**: Complete audit trail of all product changes

### 👥 User Roles

**Admin**
- Complete system access and user management
- View analytics and export capabilities
- Manage categories, sizes, and system settings
- Access to all products and edit logs

**Manager**
- Review and approve/reject product submissions
- Provide detailed rejection feedback
- View review statistics and activity logs

**Team Member**
- Submit new products for review
- Edit and resubmit rejected products
- View personal submission history and notifications

### 🔔 Notifications
- In-app notification system for status updates
- Real-time alerts for rejected products
- Direct links to edit rejected submissions

### 📊 Dashboard Features
- Role-specific dashboards with relevant metrics
- Product status tracking (Approved, Under Review, Rejected)
- Recent activity feeds and quick actions
- Search and filter capabilities

## Technology Stack

- **Backend**: Django 4.2.7 (Python 3.10+)
- **Frontend**: Bootstrap 5.1.3 + Custom CSS
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Icons**: Bootstrap Icons
- **Authentication**: Django's built-in auth system

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd upc-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create demo users and sample data
python setup_demo.py
```

### 3. Run the Application

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and login with demo credentials:

- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`  
- **Team Member**: `team` / `team123`

## Project Structure

```
upc_system/
├── accounts/           # User management and authentication
├── products/          # Core product functionality
├── notifications/     # In-app notification system
├── templates/         # HTML templates
├── static/           # CSS, JS, and static assets
├── manage.py         # Django management script
├── setup_demo.py     # Demo data creation script
└── requirements.txt  # Python dependencies
```

## Key Features in Detail

### Product Submission Workflow
1. Team members submit products with UPC codes and details
2. Products automatically enter "Under Review" status
3. Managers/Admins can approve or reject with reasons
4. Rejected products can be edited and resubmitted
5. All actions are logged for audit purposes

### Dynamic Product Attributes
- Add custom key-value pairs (e.g., "Country of Origin: United States")
- Flexible attribute system for any product type
- Easy management through the web interface

### Advanced Admin Features
- User management with role assignment
- Category and size management
- Comprehensive edit logs with filtering
- CSV export with custom filters
- System analytics and reporting

### Mobile-Responsive Design
- Clean, modern interface built with Bootstrap
- Collapsible sidebar navigation
- Touch-friendly controls and forms
- Optimized for all device sizes

## API Endpoints

The system includes several AJAX endpoints for enhanced functionality:

- `/ajax/toggle-user-status/<id>/` - Toggle user active status
- `/notifications/mark-all-read/` - Mark all notifications as read
- `/export/` - CSV export with filters

## Security Features

- CSRF protection on all forms
- Role-based access control
- Input validation and sanitization
- Secure password requirements
- Session management

## Customization

### Adding New Roles
1. Update `ROLE_CHOICES` in `accounts/models.py`
2. Add permission checks in views
3. Create role-specific templates
4. Update navigation and dashboard logic

### Custom Product Fields
1. Add fields to `Product` model
2. Update forms and templates
3. Run migrations
4. Update admin interface if needed

## Production Deployment

### Environment Variables
Create a `.env` file with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@localhost/dbname
```

### Static Files
```bash
python manage.py collectstatic
```

### Database
For PostgreSQL production setup:

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'upc_system',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Testing

Run the test suite:

```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the documentation
2. Review existing GitHub issues
3. Create a new issue with detailed information

---

**Built with Django and modern web technologies for efficient product management workflows.**
