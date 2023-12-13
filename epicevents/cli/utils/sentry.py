from sentry_sdk import set_context, capture_message


def set_user_context(key, user):
    set_context(
        key, {
            "id": user.id,
            "first_name": user.first_name.capitalize(),
            "last_name": user.last_name.capitalize(),
            "department": user.groups.first().name
        }
    )


def capture_user_creation(user, collaborator_created):
    set_context(
        "User_created",
        {
            "by_user": {
                "id": user.id,
                "name": user.get_full_name(),
                "department": user.groups.first().name
            },
            "created_user": {
                "id": collaborator_created.id,
                "name": collaborator_created.get_full_name(),
                "department": collaborator_created.groups.first().name
            }
        }
    )
    capture_message(
        f"User {user.first_name.capitalize()} {user.last_name.capitalize()}"
        f" has created user {collaborator_created.first_name.capitalize()}"
        f" {collaborator_created.last_name.capitalize()}."
    )


def capture_user_update(user, collaborator_updated, fields_changed):
    set_context(
        "User_updated",
        {
            "by_user": {
                "id": user.id,
                "name": user.get_full_name(),
                "department": user.groups.first().name
            },
            "updated_user": {
                "id": collaborator_updated.id,
                "name": collaborator_updated.get_full_name(),
                "department": collaborator_updated.groups.first().name
            },
            "fields_changed": fields_changed
        }
    )
    capture_message(
        f"User {user.first_name.capitalize()} {user.last_name.capitalize()}"
        f" has updated user {collaborator_updated.first_name.capitalize()}"
        f" {collaborator_updated.last_name.capitalize()}."
    )


def capture_contract_signed(contract):
    set_context(
        "Contract", {
            "id": contract.id,
            "client": {
                "id": contract.client.id,
                "Name": contract.client.get_full_name()
            },
            "contact": {
                "id": contract.client.contact.id,
                "Name": contract.client.contact.get_full_name()
            },
            "signed": contract.signed
        }
    )
    capture_message(
        f"Contract {contract.id} signed by client"
        f" {contract.client.first_name.capitalize()}"
        f" {contract.client.last_name.capitalize()}."
    )


def capture_user_deleted(user, collaborator_deleted):
    set_context(
        "User_deleted",
        {
            "by_user": {
                "id": user.id,
                "name": user.get_full_name(),
                "department": user.groups.first().name
            },
            "deleted_user": {
                "id": collaborator_deleted.id,
                "name": collaborator_deleted.get_full_name(),
                "department": collaborator_deleted.groups.first().name
            }
        }
    )
    capture_message(
        f"User {user.first_name.capitalize()} {user.last_name.capitalize()}"
        f" has deleted user {collaborator_deleted.first_name.capitalize()}"
        f" {collaborator_deleted.last_name.capitalize()}."
    )