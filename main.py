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
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

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
        
        logger.info('query %s' % event.get_argument())
        result = subprocess.run(["mlocate", "-i", "-b", "-l", "5", "-d", "/home/kafunkajunk/home.db", event.get_argument()], capture_output=True, text=True)
        result = result.stdout.splitlines()
        logger.info('result: %s' % result)
        range_len = len(result) if len(result) <= 5 else 5

        for index in range(range_len):

            item = result[index]
            title = ""
            logger.info('isdir %s' % os.path.isdir(item) )
            logger.info('normpath %s' % os.path.normpath(item))
            title = os.path.basename(os.path.normpath(item)) if os.path.isdir(item) else os.path.basename(item)

            data = {'path': item}
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=title,
                                             description=item,
                                             on_enter=ExtensionCustomAction(data, keep_app_open=True)))
            
            #item_name = extension.preferences['item_name']
            #data = {'new_name': '%s %s was clicked' % (item_name, i)}
            #items.append(ExtensionResultItem(icon='images/icon.png',
            #                                 name='%s %s' % (item_name, i),
            #                                 description='Tits:  %s' % result[i],
            #                                 on_enter=ExtensionCustomAction(data, keep_app_open=True)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def build_actions(path):

        yield ['echo', path, 'xclip', '-sel', 'clip']
        yield ['thunar', path]

    def execute_action(action_args):
        subprocess.run(action_args)
        HideWindowAction()
        
        
    def on_event(self, event, extension):

        data = event.get_data()
        results = [ for x in build_actions(data['path']:
            ExtensionResultItem(icon='images/icon.png', name=data['path'], on_enter=execute_action(x)) ]
        
        return RenderResultListAction(results)


if __name__ == '__main__':
    FileFinder().run()
