from django.db import models

class Product(models.Model):
    cat=[('male','male'),('female','female'),('kids','kids')]
    name=models.CharField(max_length=50)
    price=models.DecimalField(max_digits= 10,decimal_places=2)
    description=models.CharField(max_length=255)
    image=models.FileField(upload_to='images/',default='images/default.jpg')
    brand=models.CharField(max_length=30)
    category=models.CharField(max_length=10,default='',choices=cat)
    type=models.CharField(max_length=30)

    def __str__(self):
        return  self.name
    
class User(models.Model):
    user=models.CharField(max_length=50)
    email=models.EmailField(max_length=100,unique=True)
    password=models.CharField(max_length=255)
    # location=models.CharField(max_length=100)
    # contactno=models.CharField(max_length=20)

    def __str__(self):
        return self.user
     
class Cart(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)

    def item_total(self):
        return self.Product.price * self.qty

    def __str__(self):
        return f"{self.customer.username} - {self.Product.name}"

    

class EmailOtp(models.Model):
    email=models.EmailField()
    otp=models.CharField(max_length=6)
    created_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.otp}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    image = models.FileField(upload_to='profile_images/', default='profile_images/default.png')

    def __str__(self):
        return self.user.user
