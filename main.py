import json
import csv
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import re

class DataModel(ABC):
    def __init__(self, id: int):
        self.id = id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class Note(DataModel):
    def __init__(self, id: int, title: str, content: str, timestamp: str):
        super().__init__(id)
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'timestamp': self.timestamp
        }

class Task(DataModel):
    def __init__(self, id: int, title: str, description: str, priority: str, due_date: str, done: bool = False):
        super().__init__(id)
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.done = done

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date,
            'done': self.done
        }

class Contact(DataModel):
    def __init__(self, id: int, name: str, phone: str, email: str):
        super().__init__(id)
        self.name = name
        self.phone = phone
        self.email = email

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }

class FinanceRecord(DataModel):
    def __init__(self, id: int, amount: float, category: str, date: str, description: str):
        super().__init__(id)
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'description': self.description
        }

class ValidationError(Exception):
    pass

class Validator:
    @staticmethod
    def validate_date(date_str: str, with_time: bool = False) -> bool:
        try:
            if with_time:
                datetime.datetime.strptime(date_str, "%d-%m-%Y %H:%M:%S")
            else:
                datetime.datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        pattern = r'^\+?[\d\s-]{10,}$'
        return bool(re.match(pattern, phone))

class DataManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.data: List[Dict] = self.load_data()

    def load_data(self) -> List[Dict]:
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_item(self, item: DataModel):
        self.data.append(item.to_dict())
        self.save_data()

    def get_item(self, id: int) -> Optional[Dict]:
        return next((item for item in self.data if item['id'] == id), None)

    def update_item(self, id: int, updated_data: Dict):
        for i, item in enumerate(self.data):
            if item['id'] == id:
                self.data[i].update(updated_data)
                self.save_data()
                return True
        return False

    def delete_item(self, id: int) -> bool:
        initial_length = len(self.data)
        self.data = [item for item in self.data if item['id'] != id]
        if len(self.data) < initial_length:
            self.save_data()
            return True
        return False

    def export_to_csv(self, filename: str):
        if not self.data:
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

    def import_from_csv(self, filename: str):
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                self.data.extend(list(reader))
            self.save_data()
            return True
        except FileNotFoundError:
            return False

    def search_items(self, keyword: str) -> List[Dict]:
        return [item for item in self.data 
                if any(str(value).lower().find(keyword.lower()) != -1 
                      for value in item.values())]

class Calculator:
    @staticmethod
    def calculate(expression: str) -> float:
        allowed_chars = set('0123456789.+-*/() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters in expression")
        
        try:
            return eval(expression, {"__builtins__": {}})
        except (SyntaxError, NameError, ZeroDivisionError):
            raise ValueError("Invalid expression")

class PersonalAssistant:
    def __init__(self):
        self.notes = DataManager('notes.json')
        self.tasks = DataManager('tasks.json')
        self.contacts = DataManager('contacts.json')
        self.finances = DataManager('finance.json')
        self.calculator = Calculator()
        self.validator = Validator()

    def run(self):
        while True:
            self._print_main_menu()
            choice = input("Ваш выбор: ")

            if choice == '1':
                self.manage_notes()
            elif choice == '2':
                self.manage_tasks()
            elif choice == '3':
                self.manage_contacts()
            elif choice == '4':
                self.manage_finances()
            elif choice == '5':
                self.use_calculator()
            elif choice == '6':
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _print_main_menu(self):
        print("\nДобро пожаловать в Персональный помощник!")
        print("Выберите действие:")
        print("1. Управление заметками")
        print("2. Управление задачами")
        print("3. Управление контактами")
        print("4. Управление финансовыми записями")
        print("5. Калькулятор")
        print("6. Выход")

    def manage_notes(self):
        while True:
            print("\nУправление заметками:")
            print("1. Добавить заметку")
            print("2. Просмотреть заметки")
            print("3. Редактировать заметку")
            print("4. Удалить заметку")
            print("5. Экспорт в CSV")
            print("6. Импорт из CSV")
            print("7. Назад")

            choice = input("Ваш выбор: ")

            if choice == '1':
                self._add_note()
            elif choice == '2':
                self._view_notes()
            elif choice == '3':
                self._edit_note()
            elif choice == '4':
                self._delete_note()
            elif choice == '5':
                self._export_notes()
            elif choice == '6':
                self._import_notes()
            elif choice == '7':
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _add_note(self):
        title = input("Введите заголовок: ")
        content = input("Введите содержание: ")
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        note = Note(len(self.notes.data) + 1, title, content, timestamp)
        self.notes.add_item(note)
        print("Заметка добавлена!")

    def _view_notes(self):
        if not self.notes.data:
            print("Заметок нет.")
            return
        
        for note in self.notes.data:
            print(f"\nID: {note['id']}")
            print(f"Заголовок: {note['title']}")
            print(f"Содержание: {note['content']}")
            print(f"Дата: {note['timestamp']}")

    def _edit_note(self):
        note_id = int(input("Введите ID заметки: "))
        note = self.notes.get_item(note_id)
        if not note:
            print("Заметка не найдена.")
            return

        title = input("Новый заголовок (Enter - оставить прежний): ")
        content = input("Новое содержание (Enter - оставить прежнее): ")
        
        if title:
            note['title'] = title
        if content:
            note['content'] = content
        
        note['timestamp'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.notes.update_item(note_id, note)
        print("Заметка обновлена!")

    def _delete_note(self):
        note_id = int(input("Введите ID заметки: "))
        if self.notes.delete_item(note_id):
            print("Заметка удалена!")
        else:
            print("Заметка не найдена.")

    def _export_notes(self):
        filename = input("Введите имя файла для экспорта: ")
        if not filename.endswith('.csv'):
            filename += '.csv'
        self.notes.export_to_csv(filename)
        print(f"Данные экспортированы в {filename}")

    def _import_notes(self):
        filename = input("Введите имя файла для импорта: ")
        if self.notes.import_from_csv(filename):
            print("Данные импортированы успешно!")
        else:
            print("Ошибка при импорте данных.")

    def manage_tasks(self):
        while True:
            print("\nУправление задачами:")
            print("1. Добавить задачу")
            print("2. Просмотреть задачи")
            print("3. Отметить задачу как выполненную")
            print("4. Редактировать задачу")
            print("5. Удалить задачу")
            print("6. Экспорт в CSV")
            print("7. Импорт из CSV")
            print("8. Назад")

            choice = input("Ваш выбор: ")

            if choice == '1':
                self._add_task()
            elif choice == '2':
                self._view_tasks()
            elif choice == '3':
                self._mark_task_done()
            elif choice == '4':
                self._edit_task()
            elif choice == '5':
                self._delete_task()
            elif choice == '6':
                self._export_tasks()
            elif choice == '7':
                self._import_tasks()
            elif choice == '8':
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _add_task(self):
        title = input("Введите название задачи: ")
        description = input("Введите описание задачи: ")
        
        while True:
            priority = input("Выберите приоритет (Высокий/Средний/Низкий): ").capitalize()
            if priority in ['Высокий', 'Средний', 'Низкий']:
                break
            print("Некорректный приоритет. Попробуйте снова.")

        while True:
            due_date = input("Введите срок выполнения (ДД-ММ-ГГГГ): ")
            if self.validator.validate_date(due_date):
                break
            print("Некорректная дата. Используйте формат ДД-ММ-ГГГГ.")

        task = Task(len(self.tasks.data) + 1, title, description, priority, due_date)
        self.tasks.add_item(task)
        print("Задача добавлена!")

    def _view_tasks(self):
        if not self.tasks.data:
            print("Задач нет.")
            return
        
        for task in self.tasks.data:
            status = "Выполнено" if task['done'] else "В процессе"
            print(f"\nID: {task['id']}")
            print(f"Название: {task['title']}")
            print(f"Описание: {task['description']}")
            print(f"Приоритет: {task['priority']}")
            print(f"Срок: {task['due_date']}")
            print(f"Статус: {status}")

    def _mark_task_done(self):
        task_id = int(input("Введите ID задачи: "))
        task = self.tasks.get_item(task_id)
        if not task:
            print("Задача не найдена.")
            return
        
        task['done'] = True
        self.tasks.update_item(task_id, task)
        print("Задача отмечена как выполненная!")

    def _edit_task(self):
        task_id = int(input("Введите ID задачи: "))
        task = self.tasks.get_item(task_id)
        if not task:
            print("Задача не найдена.")
            return

        title = input("Новое название (Enter - оставить прежнее): ")
        if title:
            task['title'] = title

        description = input("Новое описание (Enter - оставить прежнее): ")
        if description:
            task['description'] = description

        priority = input("Новый приоритет (Высокий/Средний/Низкий или Enter - оставить прежний): ")
        if priority and priority in ['Высокий', 'Средний', 'Низкий']:
            task['priority'] = priority

        due_date = input("Новый срок (ДД-ММ-ГГГГ или Enter - оставить прежний): ")
        if due_date and self.validator.validate_date(due_date):
            task['due_date'] = due_date

        self.tasks.update_item(task_id, task)
    
    def _delete_task(self):
        task_id = int(input("Введите ID задачи: "))
        if self.tasks.delete_item(task_id):
            print("Задача удалена!")
        else:
            print("Задача не найдена.")

    def _export_tasks(self):
        filename = input("Введите имя файла для экспорта: ")
        if not filename.endswith('.csv'):
            filename += '.csv'
        self.tasks.export_to_csv(filename)
        print(f"Данные экспортированы в {filename}")

    def _import_tasks(self):
        filename = input("Введите имя файла для импорта: ")
        if self.tasks.import_from_csv(filename):
            print("Данные импортированы успешно!")
        else:
            print("Ошибка при импорте данных.")

    def manage_contacts(self):
        while True:
            print("\nУправление контактами:")
            print("1. Добавить контакт")
            print("2. Просмотреть контакты")
            print("3. Поиск контакта")
            print("4. Редактировать контакт")
            print("5. Удалить контакт")
            print("6. Экспорт в CSV")
            print("7. Импорт из CSV")
            print("8. Назад")

            choice = input("Ваш выбор: ")

            if choice == '1':
                self._add_contact()
            elif choice == '2':
                self._view_contacts()
            elif choice == '3':
                self._search_contact()
            elif choice == '4':
                self._edit_contact()
            elif choice == '5':
                self._delete_contact()
            elif choice == '6':
                self._export_contacts()
            elif choice == '7':
                self._import_contacts()
            elif choice == '8':
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _add_contact(self):
        name = input("Введите имя контакта: ")
        
        while True:
            phone = input("Введите номер телефона: ")
            if self.validator.validate_phone(phone):
                break
            print("Некорректный номер телефона.")
        
        while True:
            email = input("Введите email: ")
            if self.validator.validate_email(email):
                break
            print("Некорректный email.")

        contact = Contact(len(self.contacts.data) + 1, name, phone, email)
        self.contacts.add_item(contact)
        print("Контакт добавлен!")

    def _view_contacts(self):
        if not self.contacts.data:
            print("Контактов нет.")
            return
        
        for contact in self.contacts.data:
            print(f"\nID: {contact['id']}")
            print(f"Имя: {contact['name']}")
            print(f"Телефон: {contact['phone']}")
            print(f"Email: {contact['email']}")

    def _search_contact(self):
        keyword = input("Введите имя или номер телефона для поиска: ")
        results = self.contacts.search_items(keyword)
        
        if not results:
            print("Контакты не найдены.")
            return
        
        print("\nНайденные контакты:")
        for contact in results:
            print(f"\nID: {contact['id']}")
            print(f"Имя: {contact['name']}")
            print(f"Телефон: {contact['phone']}")
            print(f"Email: {contact['email']}")

    def _edit_contact(self):
        contact_id = int(input("Введите ID контакта: "))
        contact = self.contacts.get_item(contact_id)
        if not contact:
            print("Контакт не найден.")
            return

        name = input("Новое имя (Enter - оставить прежнее): ")
        if name:
            contact['name'] = name

        phone = input("Новый телефон (Enter - оставить прежний): ")
        if phone:
            if self.validator.validate_phone(phone):
                contact['phone'] = phone
            else:
                print("Некорректный номер телефона. Оставлен прежний номер.")

        email = input("Новый email (Enter - оставить прежний): ")
        if email:
            if self.validator.validate_email(email):
                contact['email'] = email
            else:
                print("Некорректный email. Оставлен прежний email.")

        self.contacts.update_item(contact_id, contact)
        print("Контакт обновлен!")

    def _delete_contact(self):
        contact_id = int(input("Введите ID контакта: "))
        if self.contacts.delete_item(contact_id):
            print("Контакт удален!")
        else:
            print("Контакт не найден.")

    def _export_contacts(self):
        filename = input("Введите имя файла для экспорта: ")
        if not filename.endswith('.csv'):
            filename += '.csv'
        self.contacts.export_to_csv(filename)
        print(f"Данные экспортированы в {filename}")

    def _import_contacts(self):
        filename = input("Введите имя файла для импорта: ")
        if self.contacts.import_from_csv(filename):
            print("Данные импортированы успешно!")
        else:
            print("Ошибка при импорте данных.")

    def manage_finances(self):
        while True:
            print("\nУправление финансовыми записями:")
            print("1. Добавить запись")
            print("2. Просмотреть записи")
            print("3. Поиск по категории")
            print("4. Генерация отчёта")
            print("5. Редактировать запись")
            print("6. Удалить запись")
            print("7. Экспорт в CSV")
            print("8. Импорт из CSV")
            print("9. Назад")

            choice = input("Ваш выбор: ")

            if choice == '1':
                self._add_finance_record()
            elif choice == '2':
                self._view_finance_records()
            elif choice == '3':
                self._search_finance_records()
            elif choice == '4':
                self._generate_finance_report()
            elif choice == '5':
                self._edit_finance_record()
            elif choice == '6':
                self._delete_finance_record()
            elif choice == '7':
                self._export_finance_records()
            elif choice == '8':
                self._import_finance_records()
            elif choice == '9':
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _add_finance_record(self):
        try:
            amount = float(input("Введите сумму (положительная для дохода, отрицательная для расхода): "))
            category = input("Введите категорию: ")
            
            while True:
                date = input("Введите дату (ДД-ММ-ГГГГ): ")
                if self.validator.validate_date(date):
                    break
                print("Некорректная дата. Используйте формат ДД-ММ-ГГГГ.")
            
            description = input("Введите описание: ")
            
            record = FinanceRecord(len(self.finances.data) + 1, amount, category, date, description)
            self.finances.add_item(record)
            print("Финансовая запись добавлена!")
        except ValueError:
            print("Ошибка: сумма должна быть числом.")

    def _view_finance_records(self):
        if not self.finances.data:
            print("Финансовых записей нет.")
            return
        
        total_income = sum(record['amount'] for record in self.finances.data if record['amount'] > 0)
        total_expenses = sum(record['amount'] for record in self.finances.data if record['amount'] < 0)
        balance = total_income + total_expenses

        print(f"\nОбщий баланс: {balance:.2f}")
        print(f"Общий доход: {total_income:.2f}")
        print(f"Общие расходы: {abs(total_expenses):.2f}")
        
        print("\nВсе записи:")
        for record in self.finances.data:
            print(f"\nID: {record['id']}")
            print(f"Сумма: {record['amount']}")
            print(f"Категория: {record['category']}")
            print(f"Дата: {record['date']}")
            print(f"Описание: {record['description']}")

    def _search_finance_records(self):
        category = input("Введите категорию для поиска: ")
        results = [record for record in self.finances.data if record['category'].lower() == category.lower()]
        
        if not results:
            print("Записи не найдены.")
            return
        
        total = sum(record['amount'] for record in results)
        print(f"\nОбщая сумма по категории {category}: {total:.2f}")
        
        for record in results:
            print(f"\nID: {record['id']}")
            print(f"Сумма: {record['amount']}")
            print(f"Дата: {record['date']}")
            print(f"Описание: {record['description']}")

    def _generate_finance_report(self):
        while True:
            start_date = input("Введите начальную дату (ДД-ММ-ГГГГ): ")
            if self.validator.validate_date(start_date):
                break
            print("Некорректная дата. Используйте формат ДД-ММ-ГГГГ.")

        while True:
            end_date = input("Введите конечную дату (ДД-ММ-ГГГГ): ")
            if self.validator.validate_date(end_date):
                break
            print("Некорректная дата. Используйте формат ДД-ММ-ГГГГ.")

        start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.datetime.strptime(end_date, "%d-%m-%Y")

        records = [
            record for record in self.finances.data
            if start <= datetime.datetime.strptime(record['date'], "%d-%m-%Y") <= end
        ]

        if not records:
            print("Записей за указанный период не найдено.")
            return

        income = sum(record['amount'] for record in records if record['amount'] > 0)
        expenses = sum(record['amount'] for record in records if record['amount'] < 0)
        balance = income + expenses

        print(f"\nФинансовый отчёт за период {start_date} - {end_date}:")
        print(f"Общий доход: {income:.2f}")
        print(f"Общие расходы: {abs(expenses):.2f}")
        print(f"Баланс за период: {balance:.2f}")

        # Группировка по категориям
        categories = {}
        for record in records:
            category = record['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += record['amount']

        print("\nРасходы по категориям:")
        for category, amount in categories.items():
            print(f"{category}: {amount:.2f}")

        # Сохранение отчёта в CSV
        report_filename = f"report_{start_date}_{end_date}.csv"
        with open(report_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Категория', 'Сумма'])
            for category, amount in categories.items():
                writer.writerow([category, amount])
        
        print(f"\nПодробный отчёт сохранен в файл {report_filename}")

    def _edit_finance_record(self):
        record_id = int(input("Введите ID записи: "))
        record = self.finances.get_item(record_id)
        if not record:
            print("Запись не найдена.")
            return

        try:
            amount_str = input("Новая сумма (Enter - оставить прежнюю): ")
            if amount_str:
                record['amount'] = float(amount_str)

            category = input("Новая категория (Enter - оставить прежнюю): ")
            if category:
                record['category'] = category

            date = input("Новая дата (ДД-ММ-ГГГГ или Enter - оставить прежнюю): ")
            if date:
                if self.validator.validate_date(date):
                    record['date'] = date
                else:
                    print("Некорректная дата. Оставлена прежняя дата.")

            description = input("Новое описание (Enter - оставить прежнее): ")
            if description:
                record['description'] = description

            self.finances.update_item(record_id, record)
            print("Запись обновлена!")
        except ValueError:
            print("Ошибка: сумма должна быть числом.")

    def _delete_finance_record(self):
        record_id = int(input("Введите ID записи: "))
        if self.finances.delete_item(record_id):
            print("Запись удалена!")
        else:
            print("Запись не найдена.")

    def _export_finance_records(self):
        filename = input("Введите имя файла для экспорта: ")
        if not filename.endswith('.csv'):
            filename += '.csv'
        self.finances.export_to_csv(filename)
        print(f"Данные экспортированы в {filename}")

    def _import_finance_records(self):
        filename = input("Введите имя файла для импорта: ")
        if self.finances.import_from_csv(filename):
            print("Данные импортированы успешно!")
        else:
            print("Ошибка при импорте данных.")

    def use_calculator(self):
        print("\nКалькулятор")
        print("Доступные операции: +, -, *, /")
        print("Для выхода введите 'q'")
        
        while True:
            expression = input("\nВведите выражение: ")
            if expression.lower() == 'q':
                break
            
            try:
                result = self.calculator.calculate(expression)
                print(f"Результат: {result}")
            except ValueError as e:
                print(f"Ошибка: {e}")
            except Exception as e:
                print("Произошла ошибка при вычислении.")

if __name__ == "__main__":
    assistant = PersonalAssistant()
    assistant.run()