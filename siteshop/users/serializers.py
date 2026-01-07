from rest_framework import serializers
from .models import AccessRoleRule


# class AccessRoleRuleSerializer(serializers.ModelSerializer):
#     role_name = serializers.StringRelatedField(source='role')
#     element_name = serializers.StringRelatedField(source='element')

#     class Meta:
#         model = AccessRoleRule
#         fields = "__all__"
