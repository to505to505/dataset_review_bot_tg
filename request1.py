from data_functions import *
from utilities import *
from telegram import InlineKeyboardMarkup
import pandas as pd
import os
import ast

DATA_URL = '/Users/dmitrysakharov/Documents' 
img_url = f"{DATA_URL}/dataset_review/data/img"
prepdata_url = f"{DATA_URL}/dataset_review/data/prep_data"
input_url = f"{DATA_URL}/dataset_review/data/inputs"
button_text = 122121218821827178
    
async def get_document(update, context):
    ''' Receiving data from user, downloading it and returning basic information about the dataset ''' 
    
    ID = str(update.effective_chat.id)

    await (await context.bot.get_file(update.message.document)).download(f'{input_url}/D{ID}.csv')

    data = read_data(ID)
    data_vars = get_data_variables(data, ID)

    text = f"INFORMATION ABOUT THE DATASET:\nNumber of objects (number of rows): {data_vars['n_samples']},\nNumber of features: {data_vars['n_features']}\nNumber of categorical features: {data_vars['n_cat_features']}\nNumber of numerical features: {data_vars['n_num_features']}" + "\n\nCategorical features: \n" + ', '.join(data_vars["cat_features"]) + "\n\nIncluding binary features: \n" + ', '.join(data_vars['bin_features']) + "\n\nNumerical features: \n" + ', '.join(data_vars["num_features"]) + "\n\nNumber of missing values: " + str(data_vars["n_nan"])
    await context.bot.send_message(
    chat_id = update.effective_chat.id,
    text = text
    )

    buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('Preprocess data', f'preprocess{button_text}'))
    await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
    reply_markup = InlineKeyboardMarkup(buttons))

async def get_buttons_callbacks(update, context):
    ''' Function that receives buttons replies from user and responding to them '''
    query = update.callback_query
    q_data = query.data
    await query.answer()

    if f'Descr_new{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{input_url}/D{ID}.csv", index_col=False)
        descriptive(data, ID)
        for i in range(1, 100, 1):
            if os.path.isfile(f"{img_url}/descriptive{i}_{ID}.png"): 
                await send_img(update, context, f"{img_url}/descriptive{i}_{ID}.png", filename = 'descriptive_stat')
                await remove_outputs(f"{img_url}/descriptive{i}_{ID}.png")
        buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('Preprocess data', f'preprocess{button_text}'))
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
        reply_markup = InlineKeyboardMarkup(buttons))

    elif f'Plots{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{input_url}/D{ID}.csv", index_col=False)
        graphs(data, ID)
        for v in range(0, 100, 1):
            if os.path.isfile(f"{img_url}/graphs_n_{v}_{ID}.png"): 
                await send_img(update, context, f"{img_url}/graphs_n_{v}_{ID}.png", filename=f'graphs_num_{v}')
                await remove_outputs(f"{img_url}/graphs_n_{v}_{ID}.png")

        for v in range(0, 100, 1):
            if os.path.isfile(f"{img_url}/graphs_c_{v}_{ID}.png"): 
                await send_img(update, context, f"{img_url}/graphs_c_{v}_{ID}.png", filename=f'graphs_cat_{v}')
                await remove_outputs(f"{img_url}/graphs_c_{v}_{ID}.png")
        buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('Preprocess data', f'preprocess{button_text}'))
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
        reply_markup = InlineKeyboardMarkup(buttons))

        
            
    elif f'preprocess{button_text}' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Got it! Just a second.')
        
        ID = str(update.effective_chat.id)
            
        data = pd.read_csv(f"{input_url}/D{ID}.csv")
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data, na_drops, many_drops, r_before, r_after, cat_features, num_features, bin_features = auto_preproccecing(data, data_vars, ID)
        get_data_variables(data, ID)
        
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f'Data has been preprocessed! Missing values have been imputated and some features with too little information may have been deleted.')
        
        text = f"Deleted features due to too many missing values (>70%):\n{', '.join(na_drops)}\n\n Deleted features due to too few unique categorical values per thousand values (>30/1000):\n{', '.join(many_drops)}"
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = text
        )
        
        buttons = create_buttons(('Correlation analysis', f'corr{button_text}'),
                                  ('2-samples comparison (t-test/Mann–Whitney)', f'two{button_text}'))
        
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "What do you want to do next?",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    #two-sets block     
    elif f'two{button_text}' in q_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="In order to compare two samples, you need at least one binary (two unique values) categorical feature!")
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        binary_features = data_vars["bin_features"]
        if binary_features:
            buttons = create_buttons(('t-test', f'twovt{button_text}'),
                                    ('Mann–Whitney U test', f'twovman{button_text}'))
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "What test do you want to use?",
                reply_markup = InlineKeyboardMarkup(buttons))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have binary features in your data, so I can't conduct a comparison of two samples :(")
    
    
    elif f'twovt{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data_vars["two_choice"] = "t-test"
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
        binary_features = data_vars["bin_features"]
        binary_features = [(bf, f"{bf}{button_text}") for bf in binary_features]
        buttons = create_buttons(*binary_features)
        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Pick a binary feature for comparison.",
                reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'twovman{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data_vars["two_choice"] = "mann–whitney"
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
        binary_features = data_vars["bin_features"]
        binary_features = [(bf, f"{bf}{button_text}") for bf in binary_features]
        buttons = create_buttons(*binary_features)
        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Pick a binary feature for comparison.",
                reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'corr{button_text}' in q_data:
        buttons = create_buttons(
                                  ('Pearson (parametric test)', f'pirson{button_text}'),
                                  ('Spearman (nonparametric test)', f'sperman{button_text}'))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "What correlation coefficient are you interested in?",
            reply_markup = InlineKeyboardMarkup(buttons))

            
    elif f'sperman{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=False)
        
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        
        get_corr_spearman(data, data_vars, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        await remove_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('2-samples comparison (t-test/Mann–Whitney)', f'two{button_text}' ))
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
        reply_markup = InlineKeyboardMarkup(buttons))
            
    elif f'pirson{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=False)
        
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        
        get_corr_pearson(data, data_vars, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png") 
        await remove_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('2-samples comparison (t-test/Mann–Whitney)', f'two{button_text}' ))
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
        reply_markup = InlineKeyboardMarkup(buttons))
                
    
            
    else:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
            
        BF = data_vars["bin_features"]  
              
        for bf in BF:
            if f"{bf}{button_text}" in q_data:
                
                try:
                    choice = data_vars["two_choice"]
                except:
                    choice = ""
                    
                ID = update.effective_chat.id 
                data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=False)
            
                if choice == "t-test":
                    get_ttest(data, ID, bf)
                elif choice == "mann–whitney":
                    get_manna(data, ID, bf)
                
                try:    
                    await send_file(update, context, f"{prepdata_url}/twov{ID}.csv", f"2sample_{choice}_{bf}.csv")
                    await remove_outputs(f"{prepdata_url}/twov{ID}.csv")
                    buttons = create_buttons(('Descriptive statistics of numeric features', f'Descr_new{button_text}'), ('Variable Distribution Plots *', f'Plots{button_text}'), ('Correlation analysis', f'corr{button_text}' ))
                    await context.bot.send_message(chat_id = update.effective_chat.id, text = f"What's next?\n * Drawing plots may take some time, especially if you have many variables and rows :(", 
                    reply_markup = InlineKeyboardMarkup(buttons))
                except:
                    pass
               

   
        

    
        
        