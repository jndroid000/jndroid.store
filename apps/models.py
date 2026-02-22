from django.conf import settings
from django.db import models
from categories.models import Category
from django.core.validators import MinValueValidator, MaxValueValidator

class App(models.Model):
    AGE_RATING_CHOICES = [
        ("3+", "3+ years"),
        ("7+", "7+ years"),
        ("12+", "12+ years"),
        ("16+", "16+ years"),
        ("18+", "18+ years"),
    ]

    # ==================== Basic Information ====================
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="apps",
        help_text="User who uploaded this app"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="apps",
        help_text="Category this app belongs to"
    )
    
    title = models.CharField(
        max_length=180,
        help_text="App name/title"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version of the title"
    )
    short_description = models.CharField(
        max_length=220,
        blank=True,
        help_text="Brief description (1 line)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the app"
    )

    # ==================== Android Version Requirements ====================
    version = models.CharField(
        max_length=40,
        blank=True,
        help_text="Current app version (e.g., 1.0.0)"
    )
    size_mb = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="APK size in megabytes"
    )
    min_api_level = models.IntegerField(
        default=21,
        help_text="Minimum Android API level required (21 = Android 5.0 Lollipop)"
    )
    target_api_level = models.IntegerField(
        default=35,
        help_text="Target Android API level (35 = Android 15 VanillaIceCream)"
    )
    
    # ==================== Android Details ====================
    min_android_version = models.CharField(
        max_length=10,
        default="5.0",
        help_text="Minimum Android version (e.g., 5.0, 6.0, 7.0)"
    )
    target_android_version = models.CharField(
        max_length=10,
        default="15.0",
        help_text="Target Android version (e.g., 13.0, 14.0, 15.0)"
    )

    # ==================== Media ====================
    cover_image = models.ImageField(
        upload_to="app_covers/",
        blank=True,
        null=True,
        help_text="App cover/thumbnail image"
    )
    
    # ==================== Download Options ====================
    apk_file = models.FileField(
        upload_to="apks/",
        blank=True,
        null=True,
        help_text="Direct APK file for download"
    )
    download_link = models.URLField(
        blank=True,
        help_text="External download link (Google Drive, etc)"
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash of APK for verification"
    )
    
    # ==================== Developer Information ====================
    developer_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Developer/Publisher name"
    )
    developer_email = models.EmailField(
        blank=True,
        help_text="Developer email"
    )
    support_email = models.EmailField(
        blank=True,
        help_text="Support/Contact email"
    )
    website_url = models.URLField(
        blank=True,
        help_text="Developer website"
    )
    
    # ==================== Store Information ====================
    store_name = models.CharField(
        max_length=100,
        blank=True,
        default="JnDroid Store",
        help_text="Store name (for credits)"
    )
    store_email = models.EmailField(
        blank=True,
        help_text="Store contact email"
    )
    
    # ==================== Legal & Compliance ====================
    privacy_policy_url = models.URLField(
        blank=True,
        help_text="Privacy policy URL"
    )
    terms_url = models.URLField(
        blank=True,
        help_text="Terms of service URL"
    )

    # ==================== Monetization ====================
    is_free = models.BooleanField(
        default=True,
        help_text="Is this app free?"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Price in USD (if not free)"
    )
    has_iap = models.BooleanField(
        default=False,
        help_text="Has in-app purchases?"
    )
    
    # ==================== Content Classification ====================
    age_rating = models.CharField(
        max_length=10,
        choices=AGE_RATING_CHOICES,
        default="3+",
        help_text="Appropriate age rating"
    )
    
    # ==================== Metrics & Analytics ====================
    downloads = models.PositiveIntegerField(
        default=0,
        help_text="Total download count"
    )
    install_count = models.PositiveIntegerField(
        default=0,
        help_text="Estimated install count"
    )
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average user rating (0-5)"
    )
    total_ratings = models.PositiveIntegerField(
        default=0,
        help_text="Total number of ratings"
    )
    
    # ==================== Source & Attribution ====================
    source_url = models.URLField(
        blank=True,
        help_text="Original source/home page of the app"
    )

    # ==================== Status ====================
    is_published = models.BooleanField(
        default=True,
        help_text="Is this app published/visible?"
    )
    is_pending_deletion = models.BooleanField(
        default=False,
        help_text="Marked for deletion?"
    )
    
    # ==================== Copyright & Legal ====================
    copyright_statement = models.TextField(
        blank=True,
        default="This app is the original creation of the developer listed above.",
        help_text="Copyright claim statement"
    )
    is_original_content = models.BooleanField(
        default=True,
        help_text="I confirm this is original content and I have rights to distribute it"
    )
    copyright_verified = models.BooleanField(
        default=False,
        help_text="Admin verified copyright claims"
    )
    has_copyright_claim = models.BooleanField(
        default=False,
        help_text="Does this app have a copyright/DMCA claim against it?"
    )
    copyright_claim_reason = models.TextField(
        blank=True,
        help_text="Reason for copyright claim if applicable"
    )
    takedown_requested = models.BooleanField(
        default=False,
        help_text="Owner requested takedown?"
    )
    takedown_reason = models.TextField(
        blank=True,
        help_text="Reason for owner-requested takedown"
    )
    takedown_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When takedown was requested"
    )
    
    # ==================== Copyright Registration & Verification ====================
    COPYRIGHT_PROTECTION_CHOICES = [
        ('basic', 'Basic - Developer Statement Only'),
        ('standard', 'Standard - Admin Verified'),
        ('premium', 'Premium - Registered & Verified'),
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('proprietary', 'Proprietary/Commercial'),
        ('mit', 'MIT License'),
        ('gpl', 'GPL License'),
        ('apache', 'Apache License'),
        ('bsd', 'BSD License'),
        ('custom', 'Custom License'),
        ('public_domain', 'Public Domain'),
    ]
    
    copyright_registration_number = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        help_text="Official copyright/trademark registration number"
    )
    
    copyright_holder_email = models.EmailField(
        blank=True,
        help_text="Email of copyright holder for verification"
    )
    
    copyright_holder_verified = models.BooleanField(
        default=False,
        help_text="Copyright holder email verified?"
    )
    
    copyright_protection_level = models.CharField(
        max_length=20,
        choices=COPYRIGHT_PROTECTION_CHOICES,
        default='basic',
        help_text="Level of copyright protection"
    )
    
    copyright_license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPE_CHOICES,
        default='proprietary',
        help_text="Type of license/copyright protection"
    )
    
    copyright_license_url = models.URLField(
        blank=True,
        help_text="URL to license details or full license text"
    )
    
    copyright_expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="When copyright protection expires (if applicable)"
    )
    
    copyright_notice_required = models.BooleanField(
        default=True,
        help_text="Must show copyright notice in app"
    )
    
    copyright_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_apps",
        help_text="Admin who verified copyright"
    )
    
    copyright_verified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When copyright was verified by admin"
    )
    
    copyright_dispute_status = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Dispute'),
            ('under_investigation', 'Under Investigation'),
            ('disputed', 'Disputed/Contested'),
            ('resolved', 'Resolved'),
        ],
        default='none',
        help_text="Current dispute status"
    )
    
    has_infringement_report = models.BooleanField(
        default=False,
        help_text="Has any infringement reports against this app?"
    )
    
    copyright_infringement_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of infringement reports"
    )
    
    # ==================== Content Ownership & Source Verification ====================
    CONTENT_OWNERSHIP_CHOICES = [
        ('original', 'I am the original creator'),
        ('permission', 'I have legal permission to share'),
        ('informational', 'Sharing for informational purposes'),
    ]
    
    content_ownership_type = models.CharField(
        max_length=20,
        choices=CONTENT_OWNERSHIP_CHOICES,
        default='informational',
        help_text="Declare your rights/ownership of this content"
    )
    
    play_store_link = models.URLField(
        blank=True,
        null=True,
        help_text="Link to app on Google Play Store (if available)"
    )
    
    developer_website = models.URLField(
        blank=True,
        null=True,
        help_text="Official developer website or portfolio"
    )
    
    verified_external_link = models.BooleanField(
        default=False,
        help_text="Admin verified the external link (Play Store or official website)"
    )
    
    source_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_verified_apps",
        help_text="Admin who verified the source"
    )
    
    source_verified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When source was verified"
    )
    
    # Platform compliance tracking
    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk - Verified Source'),
        ('medium', 'Medium Risk - Unverified Source'),
        ('high', 'High Risk - Requires Investigation'),
    ]
    
    legal_risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        help_text="Legal/copyright risk assessment"
    )
    
    requires_manual_review = models.BooleanField(
        default=True,
        help_text="App requires manual copyright review before publication"
    )
    
    admin_review_notes = models.TextField(
        blank=True,
        help_text="Admin notes about copyright/ownership verification"
    )
    
    release_date = models.DateField(
        auto_now_add=False,
        default='2026-01-29',
        help_text="Date when app was first published"
    )
    last_update_date = models.DateField(
        auto_now=True,
        help_text="Date of last update"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this listing was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "App"
        verbose_name_plural = "Apps"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['avg_rating']),
            models.Index(fields=['-downloads']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('apps:detail', kwargs={'slug': self.slug})


class AppScreenshot(models.Model):
    """Screenshots for app showcase"""
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="screenshots",
        help_text="App this screenshot belongs to"
    )
    image = models.ImageField(
        upload_to="app_screenshots/",
        help_text="Screenshot image (recommended: 1080x1920 or similar)"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption/description"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower = first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "App Screenshot"
        verbose_name_plural = "App Screenshots"
    
    def __str__(self):
        return f"{self.app.title} - Screenshot {self.order}"


class AppVersion(models.Model):
    """
    Track different versions of an app
    """
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="versions",
        help_text="App this version belongs to"
    )
    version_number = models.CharField(
        max_length=40,
        help_text="Version number (e.g., 1.0.1)"
    )
    description = models.TextField(
        blank=True,
        help_text="What's new in this version"
    )
    size_mb = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="App size in megabytes"
    )
    download_link = models.URLField(
        blank=True,
        help_text="Download link for this version"
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this version available for download?"
    )
    released_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Release date and time"
    )

    class Meta:
        ordering = ["-released_at"]
        verbose_name_plural = "App Versions"
        unique_together = ["app", "version_number"]

    def __str__(self):
        return f"{self.app.title} v{self.version_number}"

class Favorite(models.Model):
    """User's favorite/wishlist apps"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_apps"
    )
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "app")
        ordering = ["-added_at"]
        verbose_name_plural = "Favorites"
    
    def __str__(self):
        return f"{self.user.username} favorited {self.app.title}"


class AppDownload(models.Model):
    """Track app downloads for user history"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="app_downloads"
    )
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="downloads_by"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ["-downloaded_at"]
        indexes = [
            models.Index(fields=['user', '-downloaded_at']),
            models.Index(fields=['app', '-downloaded_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} downloaded {self.app.title}"


class CopyrightClaim(models.Model):
    """
    Track DMCA/Copyright claims and takedown requests
    For both external DMCA claims and owner-requested takedowns
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Takedown Approved'),
        ('rejected', 'Rejected - No Action Taken'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('appealed', 'Counter-Notice Filed (Appealed)'),
    ]
    
    CLAIM_TYPE_CHOICES = [
        ('dmca', 'DMCA Takedown Notice'),
        ('owner_request', 'Owner Requested Takedown'),
        ('counter_notice', 'Counter-Notice'),
    ]
    
    # App being claimed/removed
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="copyright_claims",
        help_text="App being claimed"
    )
    
    # Claim details
    claim_type = models.CharField(
        max_length=20,
        choices=CLAIM_TYPE_CHOICES,
        default='dmca',
        help_text="Type of claim"
    )
    
    # Claimant information
    claimant_name = models.CharField(
        max_length=200,
        help_text="Name of person/organization filing claim"
    )
    claimant_email = models.EmailField(
        help_text="Claimant email"
    )
    claimant_address = models.TextField(
        blank=True,
        help_text="Claimant address"
    )
    
    # Description
    description = models.TextField(
        help_text="Description of copyrighted work being infringed"
    )
    reason = models.TextField(
        help_text="Reason for claim (detailed explanation)"
    )
    
    # Evidence
    evidence_url = models.URLField(
        blank=True,
        help_text="URL to original/competing work"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Claim status"
    )
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes from admin review"
    )
    
    # Action taken
    action_taken = models.TextField(
        blank=True,
        help_text="What action was taken (if any)"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Copyright Claim"
        verbose_name_plural = "Copyright Claims"
        indexes = [
            models.Index(fields=['app', '-submitted_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_claim_type_display()} - {self.app.title} ({self.status})"


class CopyrightInfringementReport(models.Model):
    """
    User reports of potential copyright infringement
    Anyone can report if they believe an app violates copyright
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('verified', 'Verified - Infringement Confirmed'),
        ('dismissed', 'Dismissed - No Infringement'),
        ('resolved', 'Resolved'),
    ]
    
    # Reported app
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="infringement_reports",
        help_text="App being reported"
    )
    
    # Reporter information
    reporter_name = models.CharField(
        max_length=200,
        help_text="Name of person reporting"
    )
    reporter_email = models.EmailField(
        help_text="Reporter email"
    )
    
    # Report details
    title = models.CharField(
        max_length=255,
        help_text="Brief title of the report"
    )
    description = models.TextField(
        help_text="Detailed description of infringement"
    )
    
    # Original/Competing Work
    original_app_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of original app (if applicable)"
    )
    original_app_url = models.URLField(
        blank=True,
        help_text="Link to original work"
    )
    
    # Evidence
    evidence_description = models.TextField(
        blank=True,
        help_text="Specific details about what was copied"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        help_text="Report status"
    )
    
    # Admin review
    admin_notes = models.TextField(
        blank=True,
        help_text="Admin's investigation notes"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Copyright Infringement Report"
        verbose_name_plural = "Copyright Infringement Reports"
        indexes = [
            models.Index(fields=['app', '-submitted_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Infringement Report: {self.app.title} ({self.status})"


class CopyrightDisputeResolution(models.Model):
    """
    Manage disputes between app owner and copyright claimants
    """
    RESOLUTION_STATUS_CHOICES = [
        ('open', 'Open - Awaiting Resolution'),
        ('negotiation', 'Under Negotiation'),
        ('mediation', 'Mediation In Progress'),
        ('resolved_agree', 'Resolved - Both Parties Agree'),
        ('resolved_takedown', 'Resolved - App Removed'),
        ('resolved_other', 'Resolved - Other Outcome'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Related claim and app
    copyright_claim = models.OneToOneField(
        CopyrightClaim,
        on_delete=models.CASCADE,
        related_name="dispute_resolution",
        help_text="Associated copyright claim"
    )
    
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="disputes",
        help_text="App in dispute"
    )
    
    # Description
    description = models.TextField(
        help_text="Description of the dispute"
    )
    
    # Resolution attempt
    resolution_status = models.CharField(
        max_length=20,
        choices=RESOLUTION_STATUS_CHOICES,
        default='open',
        help_text="Current dispute resolution status"
    )
    
    # Terms (if resolved)
    resolution_terms = models.TextField(
        blank=True,
        help_text="Agreed upon resolution terms"
    )
    
    # Communication
    last_communication = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last communication with parties"
    )
    
    # Admin handling
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispute_cases",
        help_text="Admin assigned to handle dispute"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Copyright Dispute Resolution"
        verbose_name_plural = "Copyright Dispute Resolutions"
    
    def __str__(self):
        return f"Dispute: {self.app.title} ({self.resolution_status})"


class CopyrightVerificationToken(models.Model):
    """
    Email verification tokens for copyright holder verification
    """
    app = models.OneToOneField(
        App,
        on_delete=models.CASCADE,
        related_name="copyright_verification",
        help_text="App being verified"
    )
    
    token = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique verification token"
    )
    
    email = models.EmailField(
        help_text="Email to verify"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Has email been verified?"
    )
    
    attempts = models.PositiveIntegerField(
        default=0,
        help_text="Verification attempts made"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text="Token expiration time")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Copyright Verification Token"
        verbose_name_plural = "Copyright Verification Tokens"
    
    def __str__(self):
        return f"Verification Token: {self.app.title} ({self.email})"
