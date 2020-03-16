import json
import logging
import subprocess
import os 
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.OpenAction import OpenAction

logger = logging.getLogger(__name__)


class FileFinder(Extension):

    def __init__(self):
        super(FileFinder, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        logger.info('preferences %s' % json.dumps(extension.preferences))
        db_path = extension.preferences['fi_path']

        query = event.get_argument()
        if query == None:
            return 

        logger.info('query %s' % query)
        logger.info('db_path %s' % db_path)
        result = subprocess.run(["mlocate", "-i", "-b", "-l", "5", "-d", db_path, query], capture_output=True, text=True)
        result = result.stdout.splitlines()
        range_len = len(result) if len(result) <= 5 else 5

        for index in range(range_len):

            item = result[index]
            title = ""
            logger.info('isdir %s' % os.path.isdir(item) )
            logger.info('normpath %s' % os.path.normpath(item))
            title = os.path.basename(os.path.normpath(item)) if os.path.isdir(item) else os.path.basename(item)

            data = {'path': item}
            items.append(ExtensionResultItem(icon='images/papirus-gear-128.png',
                name=title,
                description=item,
                on_enter=ExtensionCustomAction(data, keep_app_open=True)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def __init__(self):
        super(ItemEnterEventListener, self).__init__()


    def build_actions(self, path):
        yield ('Open', OpenAction(path))
        yield ('Copy Path', CopyToClipboardAction(path))


    def on_event(self, event, extension):

        data = event.get_data()
        path = data['path']

        results = []
        for item in self.build_actions(path):

            (verb, action) = item
            results.append(ExtensionResultItem(icon='images/papirus-gear-128.png', name='{verb} {path}'.format(verb=verb, path=path), on_enter=action) )

        return RenderResultListAction(results)



if __name__ == '__main__':
    FileFinder().run()
