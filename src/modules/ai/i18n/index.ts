// AI module i18n - English
export const aiEn = {
  ai: {
    chat: {
      title: 'AI Assistant',
      description: 'Chat with AI assistant to get help with your gear items',
      context: 'Context',
      showContextConfig: 'Show context configuration',
      clearMessages: 'Clear messages',
      startConversation: 'Start a conversation with AI...',
      thinking: 'AI is thinking...',
      placeholder: 'Ask AI about your gear...',
      send: 'Send message',
      sendHint: 'Ctrl+Enter to send',
      includeContainerData: {
        tooltip: 'Include container items in context',
        label: 'Include items'
      },
      templateMessages: {
        addRandomItem: {
          label: 'Add a random item',
          prompt: 'Add a random item to my bag (lighter 5g, multitool, etc.). Don\'t ask, just add.',
        },
        whatsUnnecessary: {
          label: 'What is unnecessary?',
          prompt: 'What is unnecessary in my bag?',
        },
        whatsNeeded: {
          label: 'What would you add?',
          prompt: 'What would you add to my bag?',
        },
      },
      history: {
        title: 'History',
        empty: 'No history',
        restore: 'Restore',
        openHistory: 'Open history',
      },
    },
    model: {
      selectPlaceholder: 'Select model',
      selectTooltip: 'Select AI model',
    },
    models: {
      loadError: 'Failed to load AI models',
    },
    settings: {
      loadError: 'Failed to load AI settings',
    },
    context: {
      fields: 'Context Fields',
      description: 'Select which fields to include when sending data to AI',
    },
    cost: {
      tokens: 'Tokens:',
      cost: 'Cost:',
      in: 'in',
      out: 'out',
    },
    premium: {
      title: 'Premium Feature',
      description: 'AI settings are available for Premium users',
      ownTokenOption: 'Alternatively, configure your own OpenRouter API token in Settings to use AI features for free.',
      modelSelectorDisabled: 'Model selection requires Premium',
      contextConfigDisabled: 'Context configuration requires Premium',
    },
    actions: {
      error: 'Failed to execute AI action',
      noContainer: 'No container specified for this action',
      containerNotFound: 'Container not found',
      invalidData: 'Invalid data received from AI',
      itemCreated: 'Item "{name}" created successfully',
      itemUpdated: 'Item updated successfully',
      itemDeleted: 'Item deleted successfully',
      containerCreated: 'Container "{name}" created successfully',
    },
    history: {
      title: 'AI History',
      empty: 'No history yet',
      restore: 'Restore conversation',
      delete: 'Delete',
      deleteAll: 'Delete all',
      confirmDelete: 'Are you sure you want to delete this conversation?',
      confirmDeleteAll: 'Are you sure you want to delete all conversations? This action cannot be undone.',
      filters: {
        operationType: 'Operation type',
        search: 'Search',
        all: 'All',
      },
      operationTypes: {
        chat: 'Chat',
        classify: 'Classify',
        analyze: 'Analyze',
        generate: 'Generate',
      },
      details: 'Details',
      back: 'Back',
      model: 'Model',
      provider: 'Provider',
      tokens: 'Tokens',
      cost: 'Cost',
      duration: 'Duration',
      createdAt: 'Created at',
      operationType: 'Operation type',
      preview: 'Preview',
      noPreview: 'No preview available',
      resumeChat: 'Resume chat',
      viewAll: 'View all',
    },
  },
}

// AI module i18n - Polish
export const aiPl = {
  ai: {
    chat: {
      title: 'Asystent AI',
      description: 'Czatuj z asystentem AI, aby uzyskać pomoc dotyczącą swojego sprzętu',
      context: 'Kontekst',
      showContextConfig: 'Pokaż konfigurację kontekstu',
      clearMessages: 'Wyczyść wiadomości',
      startConversation: 'Rozpocznij rozmowę z AI...',
      thinking: 'AI myśli...',
      placeholder: 'Zapytaj AI o swój sprzęt...',
      send: 'Wyślij wiadomość',
      sendHint: 'Ctrl+Enter aby wysłać',
      includeContainerData: {
        tooltip: 'Dołącz przedmioty z kontenera do kontekstu',
        label: 'Dołącz przedmioty'
      },
      templateMessages: {
        addRandomItem: {
          label: 'Dodaj losowy przedmiot',
          prompt: 'Dodaj losowy przedmiot do mojego bagu (lighter 5g, multitool, etc.). Nie pytaj, po prostu dodaj.',
        },
        whatsUnnecessary: {
          label: 'Co jest niepotrzebne?',
          prompt: 'Co jest niepotrzebne w moim bagu?',
        },
        whatsNeeded: {
          label: 'Co byś dodał?',
          prompt: 'Co byś dodał do mojego bagu?',
        },
      },
      history: {
        title: 'Historia',
        empty: 'Brak historii',
        restore: 'Przywróć',
        openHistory: 'Otwórz historię',
      },
    },
    model: {
      selectPlaceholder: 'Wybierz model',
      selectTooltip: 'Wybierz model AI',
    },
    models: {
      loadError: 'Nie udało się załadować modeli AI',
    },
    settings: {
      loadError: 'Nie udało się załadować ustawień AI',
    },
    context: {
      fields: 'Pola kontekstu',
      description: 'Wybierz które pola uwzględnić podczas wysyłania danych do AI',
    },
    cost: {
      tokens: 'Tokeny:',
      cost: 'Koszt:',
      in: 'wejście',
      out: 'wyjście',
    },
    premium: {
      title: 'Funkcja Premium',
      description: 'Ustawienia AI są dostępne dla użytkowników Premium',
      ownTokenOption: 'Alternatywnie, skonfiguruj własny token API OpenRouter w Ustawieniach, aby korzystać z funkcji AI za darmo.',
      modelSelectorDisabled: 'Wybór modelu wymaga Premium',
      contextConfigDisabled: 'Konfiguracja kontekstu wymaga Premium',
    },
    actions: {
      error: 'Nie udało się wykonać akcji AI',
      noContainer: 'Nie określono kontenera dla tej akcji',
      containerNotFound: 'Nie znaleziono kontenera',
      invalidData: 'Otrzymano nieprawidłowe dane od AI',
      itemCreated: 'Przedmiot "{name}" został dodany',
      itemUpdated: 'Przedmiot został zaktualizowany',
      itemDeleted: 'Przedmiot został usunięty',
      containerCreated: 'Kontener "{name}" został utworzony',
    },
    history: {
      title: 'Historia AI',
      empty: 'Brak historii',
      restore: 'Przywróć konwersację',
      delete: 'Usuń',
      deleteAll: 'Usuń wszystkie',
      confirmDelete: 'Czy na pewno chcesz usunąć tę konwersację?',
      confirmDeleteAll: 'Czy na pewno chcesz usunąć wszystkie konwersacje? Ta akcja nie może być cofnięta.',
      filters: {
        operationType: 'Typ operacji',
        search: 'Wyszukaj',
        all: 'Wszystkie',
      },
      operationTypes: {
        chat: 'Czat',
        classify: 'Klasyfikuj',
        analyze: 'Analizuj',
        generate: 'Generuj',
      },
      details: 'Szczegóły',
      back: 'Wróć',
      model: 'Model',
      provider: 'Dostawca',
      tokens: 'Tokeny',
      cost: 'Koszt',
      duration: 'Czas trwania',
      createdAt: 'Utworzono',
      operationType: 'Typ operacji',
      preview: 'Podgląd',
      noPreview: 'Brak podglądu',
      resumeChat: 'Wznów czat',
      viewAll: 'Zobacz wszystkie',
    },
  },
}
