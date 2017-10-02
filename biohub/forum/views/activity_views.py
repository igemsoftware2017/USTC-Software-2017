from django.db import models
from rest_framework import mixins, decorators, viewsets

from biohub.forum.models import Activity
from biohub.biobrick.models import BiobrickMeta
from biohub.forum.serializers.activity_serializers import ActivitySerializer
from biohub.utils.rest import pagination, permissions


class ActivityViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    serializer_class = ActivitySerializer
    pagination_class = pagination.factory('PageNumberPagination', page_size=10)

    def get_queryset(self):

        queryset = Activity.objects.all()

        if self.action == 'timeline':
            user = self.request.user
            queryset = queryset.filter(
                models.Q(
                    user__in=models.Subquery(
                        user.following.through.objects.filter(
                            to_user_id=user.id
                        ).values('from_user_id')
                    )
                ) | (
                    models.Q(
                        brick_name__in=models.Subquery(
                            user.bricks_watching.through.objects.filter(
                                user=user.id
                            ).values('brick')
                        )
                    ) & ~models.Q(user=user.id)
                )
            )

        user = self.request.query_params.get('user', None)
        type = self.request.query_params.get('type', None)

        if user is not None:
            queryset = queryset.filter(user__username=user)
        if type is not None:
            queryset = queryset.filter(type__in=type.split(','))

        queryset = queryset.annotate(
            score=models.Case(
                models.When(
                    type='Watch',
                    then=models.Subquery(
                        BiobrickMeta.objects
                        .filter(part_name=models.OuterRef('brick_name'))
                        .values('rate_score')
                    )
                ),
                default=None
            )
        )

        return queryset.order_by('-acttime')

    @decorators.list_route(methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def timeline(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
