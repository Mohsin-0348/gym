from django.contrib import admin

from members.models import (
    Food,
    FoodsConsumed,
    FoodToEat,
    Member,
    NutritionPlan,
    TrackBodyMeasurement,
    TrackNutritionPlan,
)

admin.site.register(Food)
admin.site.register(TrackBodyMeasurement)


class FoodToEatStackedInline(admin.StackedInline):
    model = FoodToEat


@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    inlines = [FoodToEatStackedInline]
    model = NutritionPlan
    list_display = ['member', 'meal_type']


class FoodsConsumedStackedInline(admin.StackedInline):
    model = FoodsConsumed


@admin.register(TrackNutritionPlan)
class TrackNutritionPlanAdmin(admin.ModelAdmin):
    inlines = [FoodsConsumedStackedInline]
    model = TrackNutritionPlan
    list_display = ['plan', 'created_on']


admin.site.register(Member)
