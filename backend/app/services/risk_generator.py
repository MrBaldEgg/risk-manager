import uuid
import re
from typing import List, Dict
from app.models.risk import Risk, RiskCategory
from app.models.answer import Answer


class RiskGenerator:
    """
    Генератор рисков на основе ответов пользователя. (пока что поиск клюбчевых слов)
    Анализ текста - выделение категории риска на основе содержания ответа.
    
    НА БУДЕЩЕЕ - БУДЕТ РЕАЛИЗОВАНО NLP/LLM ЛОГИКА для более глубокого анализа
    """
    
    # Словарь: ключевые слова в категорию риска
    KEYWORDS_MAP: Dict[str, RiskCategory] = {
        # Кадровые риски
        "сотрудник": RiskCategory.PERSONNEL,
        "кадры": RiskCategory.PERSONNEL,
        "уволится": RiskCategory.PERSONNEL,
        "увольнение": RiskCategory.PERSONNEL,
        "команда": RiskCategory.PERSONNEL,
        "специалист": RiskCategory.PERSONNEL,
        "квалификация": RiskCategory.PERSONNEL,
        "текучесть": RiskCategory.PERSONNEL,
        "обучение": RiskCategory.PERSONNEL,
        
        # Финансовые риски
        "деньги": RiskCategory.FINANCIAL,
        "финансы": RiskCategory.FINANCIAL,
        "прибыль": RiskCategory.FINANCIAL,
        "убытки": RiskCategory.FINANCIAL,
        "кассовый разрыв": RiskCategory.FINANCIAL,
        "кредит": RiskCategory.FINANCIAL,
        "инвестиции": RiskCategory.FINANCIAL,
        "бюджет": RiskCategory.FINANCIAL,
        "налог": RiskCategory.FINANCIAL,
        "ндс": RiskCategory.FINANCIAL,
        "цена": RiskCategory.FINANCIAL,
        "дорого": RiskCategory.FINANCIAL,
        
        # Рыночные риски
        "конкурент": RiskCategory.MARKET,
        "конкуренция": RiskCategory.MARKET,
        "спрос": RiskCategory.MARKET,
        "клиент": RiskCategory.MARKET,
        "рынок": RiskCategory.MARKET,
        "продажи": RiskCategory.MARKET,
        "реклама": RiskCategory.MARKET,
        "маркетинг": RiskCategory.MARKET,
        
        # Правовые риски
        "закон": RiskCategory.LEGAL,
        "проверка": RiskCategory.LEGAL,
        "лицензия": RiskCategory.LEGAL,
        "суд": RiskCategory.LEGAL,
        "договор": RiskCategory.LEGAL,
        "регулятор": RiskCategory.LEGAL,
        "штраф": RiskCategory.LEGAL,
        
        # Операционные риски
        "поставщик": RiskCategory.OPERATIONAL,
        "логистика": RiskCategory.OPERATIONAL,
        "оборудование": RiskCategory.OPERATIONAL,
        "сбой": RiskCategory.OPERATIONAL,
        "остановка": RiskCategory.OPERATIONAL,
        "качество": RiskCategory.OPERATIONAL,
        "брак": RiskCategory.OPERATIONAL,
        "производство": RiskCategory.OPERATIONAL,
        "процесс": RiskCategory.OPERATIONAL,
        
        # ИТ-риски
        "данные": RiskCategory.IT,
        "безопасность": RiskCategory.IT,
        "взлом": RiskCategory.IT,
        "сервер": RiskCategory.IT,
        "сайт": RiskCategory.IT,
        "программа": RiskCategory.IT,
        "технология": RiskCategory.IT,
        "автоматизация": RiskCategory.IT,
        
        # Репутационные риски
        "репутация": RiskCategory.REPUTATIONAL,
        "отзыв": RiskCategory.REPUTATIONAL,
        "жалоба": RiskCategory.REPUTATIONAL,
        "скандал": RiskCategory.REPUTATIONAL,
        "соцсети": RiskCategory.REPUTATIONAL,
    }
    
    # Словарь: категория в примеры названий рисков
    RISK_TITLES: Dict[RiskCategory, List[str]] = {
        RiskCategory.PERSONNEL: [
            "Потеря ключевого сотрудника",
            "Снижение квалификации персонала",
            "Высокая текучесть кадров",
        ],
        RiskCategory.FINANCIAL: [
            "Кассовый разрыв",
            "Рост налоговой нагрузки",
            "Снижение прибыльности",
        ],
        RiskCategory.MARKET: [
            "Усиление конкуренции",
            "Падение спроса",
            "Потеря клиентов",
        ],
        RiskCategory.LEGAL: [
            "Изменение законодательства",
            "Штрафы и санкции",
            "Проблемы с лицензированием",
        ],
        RiskCategory.OPERATIONAL: [
            "Сбой поставок",
            "Поломка оборудования",
            "Снижение качества продукции",
        ],
        RiskCategory.IT: [
            "Утечка данных",
            "Кибератака",
            "Отказ ИТ-систем",
        ],
        RiskCategory.REPUTATIONAL: [
            "Негативные отзывы",
            "Потеря доверия клиентов",
            "Репутационный скандал",
        ],
    }
    
    def analyze_answers(self, answers: List[Answer]) -> List[Risk]:
        """
        Анализ ответов - генерация рисков
        answers: Список ответов пользователя
        Returns: Список сгенерированных рисков
        """
        risks: List[Risk] = []
        used_categories: set = set()
        
        for answer in answers:
            if not answer.text:
                continue
            
            text_lower = answer.text.lower()
            
            # Поиск ключевых слов в ответе
            for keyword, category in self.KEYWORDS_MAP.items():
                if keyword in text_lower and category not in used_categories:
                    risk = self._create_risk(answer.text, category, keyword)
                    risks.append(risk)
                    used_categories.add(category)
                    break  # Один риск на ответ
        
        # Если нет - то заглушка риска
        if not risks:
            risk = Risk(
                id=str(uuid.uuid4()),
                title="Неопределенный риск",
                description="Требуется дополнительный анализ. Рекомендуется консультация специалиста.",
                category=RiskCategory.MARKET,
                probability=3,
                impact=3,
            )
            risk.calculate_priority()
            risks.append(risk)
        
        return risks
    
    def _create_risk(self, answer_text: str, category: RiskCategory, keyword: str) -> Risk:
        """
        Создает объект риска на основе найденного ключевого слова.
        
        Args:
            answer_text: Текст ответа пользователя
            category: Категория риска
            keyword: Найденное ключевое слово
            
        Returns:
            Объект Risk
        """
        # Выбираем подходящее название из шаблонов
        titles = self.RISK_TITLES.get(category, ["Неопределенный риск"])
        title = titles[0]  # Пока только первое название в словаре (В БУДУЩЕМ НАДО БУДЕТ ДОБАВИТЬ УМНУЮ ТИПИЗАЦИЮ)
        
        # Базовая оценка (пользователь может изменить в матрице) / подумать может встроить в опросник!!!!
        probability = 2
        impact = 2
        
        #  Если есть тревожные слова - повышается влияние риска
        alarm_words = ["боюсь", "страшно", "катастрофа", "критично", "ужас", "страх", "нервы"]
        for word in alarm_words:
            if word in answer_text.lower():
                impact = 4
                break
        
        risk = Risk(
            id=str(uuid.uuid4()),
            title=title,
            description=answer_text[:500],  # Обрезаем до 500 символов (на всякий случай)
            category=category,
            probability=probability,
            impact=impact,
        )
        risk.calculate_priority()
        
        return risk


# Глобальный экземпляр генератора
risk_generator = RiskGenerator()