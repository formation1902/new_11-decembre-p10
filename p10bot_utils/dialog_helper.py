#
# Utilitaire pour executer un objet dialog
#
from botbuilder.core import StatePropertyAccessor, TurnContext
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus


class DialogHelper:

    @staticmethod
    async def run_dialog(dialog: Dialog, turn_context: TurnContext, accessor: StatePropertyAccessor):  
        #
        # Executer le dialog
        #
        
        dialog_set = DialogSet(accessor)
        
        dialog_set.add(dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        
        results = await dialog_context.continue_dialog()
        
        if results.status == DialogTurnStatus.Empty:
            print("#\n# INFO [ DialogHelper - run_dialog ] begin_dialog after results empty status\n#\n")
            await dialog_context.begin_dialog(dialog.id)
