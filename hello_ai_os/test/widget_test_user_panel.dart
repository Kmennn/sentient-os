import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/user_management_panel.dart';

void main() {
  final owner = User(id: '1', name: 'Alice', role: UserRole.OWNER);
  final operator = User(id: '2', name: 'Bob', role: UserRole.OPERATOR);
  final observer = User(id: '3', name: 'Charlie', role: UserRole.OBSERVER);

  final users = [owner, operator, observer];

  testWidgets('Owner sees edit controls', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UserManagementPanel(currentUser: owner, allUsers: users),
        ),
      ),
    );

    // Should see all users
    expect(find.text('Alice'), findsOneWidget);
    expect(find.text('Bob'), findsOneWidget);
    expect(find.text('Charlie'), findsOneWidget);

    // Should see Dropdown for Bob (Alice is owner, Bob is not self)
    // Flutter DropdownButton creates an internal widget structure, but we can look for the type or key if needed.
    // Simpler: Look for the absence of "Read Only" chip
    expect(find.text('Read Only'), findsNothing);

    // We expect 2 dropdowns (Bob and Charlie), Alice is self so no dropdown logic provided in code?
    // Code says: trailing: canEdit && user.id != currentUser.id ? dropdown : null
    // So Bob and Charlie should have dropdowns.
    expect(find.byType(DropdownButton<UserRole>), findsNWidgets(2));
  });

  testWidgets('Observer sees read only view', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UserManagementPanel(currentUser: observer, allUsers: users),
        ),
      ),
    );

    // Should see "Read Only"
    expect(find.text('Read Only'), findsOneWidget);

    // Should see NO dropdowns
    expect(find.byType(DropdownButton<UserRole>), findsNothing);
  });
}
