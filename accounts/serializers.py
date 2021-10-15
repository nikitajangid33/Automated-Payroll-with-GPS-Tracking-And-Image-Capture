from django.db.models import fields
from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User

class CharValidator(serializers.CharField):#validate char field , it should not empty
    def from_native(self,value):
        if value == '':
            return False
        return True

#validate username field , it should not empty and length should be min 8 and maximum can be of 16
class UsernameValidator(serializers.CharField):
    def from_native(self,value):
        if value == '':
            return False
        if len(value) < 8:
            return False
        if len(value) > 16:
            return False

        return True

#employee model serializer
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Employee
        fields='__all__'

#User model serializer
class UserSerializer(serializers.ModelSerializer):
    first_name=CharValidator(required=True)
    last_name=CharValidator(required=True)
    username=UsernameValidator(required=True)

    class Meta:
        model=User
        fields=('first_name','last_name','username',)