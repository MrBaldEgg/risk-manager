import uuid
import re
from typing import List, Set
from app.models.risk import Risk, RiskCategory
from app.models.answer import Answer


class RiskGenerator:
    """
    Генератор рисков на основе ответов пользователя.
    
    Разделяет текст на предложения/фразы,
    ищет ключевые слова в каждой фразе отдельно,
    создает структурированные риски.
    """
    
    KEYWORDS_MAP = {
        # Кадровые
        "сотрудник": RiskCategory.PERSONNEL,
        "кадры": RiskCategory.PERSONNEL,
        "уволится": RiskCategory.PERSONNEL,
        "увольнение": RiskCategory.PERSONNEL,
        "команда": RiskCategory.PERSONNEL,
        "специалист": RiskCategory.PERSONNEL,
        "квалификация": RiskCategory.PERSONNEL,
        "текучесть": RiskCategory.PERSONNEL,
        "обучение": RiskCategory.PERSONNEL,
        # Финансовые
        "деньги": RiskCategory.FINANCIAL,
        "финансы": RiskCategory.FINANCIAL,
        "прибыль": RiskCategory.FINANCIAL,
        "убытки": RiskCategory.FINANCIAL,
        "кассовый": RiskCategory.FINANCIAL,
        "кредит": RiskCategory.FINANCIAL,
        "инвестиции": RiskCategory.FINANCIAL,
        "бюджет": RiskCategory.FINANCIAL,
        "дорого": RiskCategory.FINANCIAL,
        "цена": RiskCategory.FINANCIAL,
        # Правовые
        "налог": RiskCategory.LEGAL,
        "ндс": RiskCategory.LEGAL,
        "закон": RiskCategory.LEGAL,
        "проверка": RiskCategory.LEGAL,
        "лицензия": RiskCategory.LEGAL,
        "суд": RiskCategory.LEGAL,
        "договор": RiskCategory.LEGAL,
        "штраф": RiskCategory.LEGAL,
        # Рыночные
        "конкурент": RiskCategory.MARKET,
        "конкуренция": RiskCategory.MARKET,
        "спрос": RiskCategory.MARKET,
        "клиент": RiskCategory.MARKET,
        "рынок": RiskCategory.MARKET,
        "продажи": RiskCategory.MARKET,
        "реклама": RiskCategory.MARKET,
        # Операционные
        "поставщик": RiskCategory.OPERATIONAL,
        "логистика": RiskCategory.OPERATIONAL,
        "оборудование": RiskCategory.OPERATIONAL,
        "сбой": RiskCategory.OPERATIONAL,
        "остановка": RiskCategory.OPERATIONAL,
        "качество": RiskCategory.OPERATIONAL,
        "брак": RiskCategory.OPERATIONAL,
        "производство": RiskCategory.OPERATIONAL,
        # ИТ
        "данные": RiskCategory.IT,
        "безопасность": RiskCategory.IT,
        "взлом": RiskCategory.IT,
        "сервер": RiskCategory.IT,
        "сайт": RiskCategory.IT,
        "технология": RiskCategory.IT,
        # Репутационные
        "репутация": RiskCategory.REPUTATIONAL,
        "отзыв": RiskCategory.REPUTATIONAL,
        "жалоба": RiskCategory.REPUTATIONAL,
        "скандал": RiskCategory.REPUTATIONAL,
    }
    
    RISK_TITLES = {
        RiskCategory.PERSONNEL: [
            "Потеря ключевого сотрудника",
            "Снижение квалификации персонала",
            "Высокая текучесть кадров",
        ],
        RiskCategory.FINANCIAL: [
            "Кассовый разрыв",
            "Рост расходов",
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
            "Проблемы с регулированием",
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
    
    def _split_into_phrases(self, text: str) -> List[str]:
        """
        Разделяет текст на отдельные фразы.
        
        Учитывает:
        - Точки, запятые, точки с запятой
        - Союз "и" между разными темами
        - "а также", "еще", "также" как разделители
        """
        # Заменяем разделители на |
        text = re.sub(r'\s+и\s+', '|', text)
        text = re.sub(r'\s+а также\s+', '|', text)
        text = re.sub(r'\s+еще\s+', '|', text)
        text = re.sub(r'\s+также\s+', '|', text)
        
        # Разделяем
        phrases = re.split(r'[.,;|]', text)
        
        # Очищаем и фильтруем пустые
        phrases = [p.strip() for p in phrases if p.strip()]
        
        return phrases
    
    def _find_keywords(self, text: str) -> Set[str]:
        """Находит все ключевые слова в тексте"""
        text_lower = text.lower()
        found = set()
        
        for keyword in self.KEYWORDS_MAP:
            if keyword in text_lower:
                found.add(keyword)
        
        return found
    
    def analyze_answers(self, answers: List[Answer]) -> List[Risk]:
        """
        Анализирует ответы и генерирует риски.
        
        Для каждого ответа:
        1. Разделяет на фразы
        2. В каждой фразе ищет ключевые слова
        3. Создает риск для каждой найденной категории
        """
        risks: List[Risk] = []
        used_categories: set = set()
        
        for answer in answers:
            if not answer.text:
                continue
            
            # Разделяем на фразы
            phrases = self._split_into_phrases(answer.text)
            
            for phrase in phrases:
                # Ищем ключевые слова в каждой фразе
                keywords = self._find_keywords(phrase)
                
                for keyword in keywords:
                    category = self.KEYWORDS_MAP[keyword]
                    
                    # Один риск на категорию
                    if category not in used_categories:
                        risk = self._create_risk(phrase, category, keyword)
                        risks.append(risk)
                        used_categories.add(category)
        
        # Если ничего не нашли — общий риск
        if not risks:
            risk = Risk(
                id=str(uuid.uuid4()),
                title="Неопределенный риск",
                description="Требуется дополнительный анализ.",
                category=RiskCategory.MARKET,
                probability=3,
                impact=3,
            )
            risk.calculate_priority()
            risks.append(risk)
        
        return risks
    
    def _create_risk(self, phrase: str, category: RiskCategory, keyword: str) -> Risk:
        """Создает объект риска"""
        titles = self.RISK_TITLES.get(category, ["Неопределенный риск"])
        title = titles[0]                                                       # Подумать над полноценной типизацией !!!!!!!!!!
        
        probability = 2
        impact = 2
        
        # Тревожные слова - выше оценка
        alarm_words = ["боюсь", "страшно", "катастрофа", "критично", "ужас", "переживаю", "беспокоит"]
        for word in alarm_words:
            if word in phrase.lower():
                probability = 3
                impact = 3
                break
        
        risk = Risk(
            id=str(uuid.uuid4()),
            title=title,
            description=phrase[:500],
            category=category,
            probability=probability,
            impact=impact,
        )
        risk.calculate_priority()
        
        return risk


risk_generator = RiskGenerator()