import 'package:flutter/material.dart';

enum UserRole { OWNER, OPERATOR, OBSERVER }

class User {
  final String id;
  final String name;
  final UserRole role;

  User({required this.id, required this.name, required this.role});
}

class UserManagementPanel extends StatelessWidget {
  final User currentUser;
  final List<User> allUsers;
  final Function(String userId, UserRole newRole)? onRoleChanged;

  const UserManagementPanel({
    super.key,
    required this.currentUser,
    required this.allUsers,
    this.onRoleChanged,
  });

  bool get canEdit => currentUser.role == UserRole.OWNER;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'User Authority',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                if (!canEdit)
                  const Chip(
                    label: Text('Read Only'),
                    backgroundColor: Colors.grey,
                  ),
              ],
            ),
          ),
          const Divider(),
          ListView.builder(
            shrinkWrap: true,
            itemCount: allUsers.length,
            itemBuilder: (context, index) {
              final user = allUsers[index];
              return ListTile(
                leading: CircleAvatar(child: Text(user.name[0])),
                title: Text(user.name),
                subtitle: Text(user.role.toString().split('.').last),
                trailing: canEdit && user.id != currentUser.id
                    ? _buildRoleDropdown(user)
                    : null,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildRoleDropdown(User user) {
    return DropdownButton<UserRole>(
      value: user.role,
      items: UserRole.values.map((role) {
        return DropdownMenuItem(
          value: role,
          child: Text(role.toString().split('.').last),
        );
      }).toList(),
      onChanged: (newRole) {
        if (newRole != null && onRoleChanged != null) {
          onRoleChanged!(user.id, newRole);
        }
      },
      underline: Container(),
    );
  }
}
