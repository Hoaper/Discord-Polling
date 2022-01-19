import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ButtonStyle
import static_config as cfg
import json

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=">", intents=intents)

#######################
# Embeds
# main embed message
main_embed = discord.Embed(title="Hello there it's welcome message!", description="Choose ur fraction!", color=cfg.DEFAULT_COLOR)

# selection embed message
selection_embed_1 = discord.Embed(title="When minecraft released?", description="1. 2008\n2. 2009\n3. 2011\n4. 2007", color=cfg.DEFAULT_COLOR)
selection_embed_2 = discord.Embed(title="How much mineralka cost?", description = "1. 100\n2. 180\n3. 200\n4. 500", color=cfg.DEFAULT_COLOR)
selection_embed_3 = discord.Embed(title="Which language is better?", description = "1. Python\n2. C++\n3. C#\n4. Pascal", color=cfg.DEFAULT_COLOR)
#****ENDING_EMBED*****#
ending_embed = discord.Embed(title="Congratulations!!!", color=cfg.DEFAULT_COLOR)
ending_embed.set_image(url="https://cdn.notonthehighstreet.com/fs/3f/8c/0ae0-1a57-4aa2-99bc-d6e7df631ca9/original_a-bright-patterned-congratulations-card.jpg")
#*********************#
#######################



@bot.event
async def on_ready():
    DiscordComponents(bot)
    print(f"Running as {bot.user}")


@bot.command()
async def create(ctx):
    # deleting message 
    await ctx.message.delete()

    # check for permissions manage_messages
    if ctx.author.guild_permissions.manage_messages:

        await ctx.send(embed = main_embed, components = [
            Button(label="START QUIZ", custom_id="poll", style=ButtonStyle.green)
        ])

def add_score(c_id: str, u_id: str):

    with open('results.json', 'r') as file:

        j_file = json.load(file)

        try:

            j_file[c_id][u_id] += 1

        except KeyError:    

            try:

                j_file[c_id]

            except KeyError:

                j_file[c_id] = {}
                j_file[c_id][u_id] = 1
            
            try:

                j_file[c_id][u_id]
            
            except KeyError:

                j_file[c_id][u_id] = 1


        with open('results.json', "w") as w_file:

            json.dump(j_file, w_file, indent=6)

def get_score(c_id: str, u_id: str):
    
    with open('results.json', 'r') as f:
        j_file = json.load(f)
        
        return j_file[c_id][u_id]


async def next_poll(inter):

    splitted_value = inter.values[0].split('_')

    if splitted_value[-1] == "!":

        add_score(str(inter.channel.id), str(inter.author.id))

    if splitted_value[0] == "poll1":

        await inter.send(embed = selection_embed_2, components = [
            bot.components_manager.add_callback(
                Select(
                    placeholder = "Select ur answer!",
                    options= [
                        SelectOption(label = "100", value = "poll2_2"),
                        SelectOption(label = "180", value = "poll2_!"),
                        SelectOption(label = "200", value = "poll2_1"),
                        SelectOption(label = "500", value = "poll2_0")
                    ]
                ),
                next_poll
            )
        ])

        return

    if splitted_value[0] == "poll2":

        await inter.send(embed = selection_embed_3, components = [
            bot.components_manager.add_callback(
                Select(
                    placeholder = "Select ur answer!",
                    options= [
                        SelectOption(label = "Python", value = "poll3_!"),
                        SelectOption(label = "C++", value = "poll3_2"),
                        SelectOption(label = "C#", value = "poll3_1"),
                        SelectOption(label = "Pascal", value = "poll3_0")
                    ]
                ),
                next_poll
            )
        ])
        return

    # the end of poll
    if splitted_value[0] == "poll3":


        score = get_score(str(inter.channel.id), str(inter.author.id))

        with open('roles.json', "r") as f:
            roles = json.load(f)
            try:
                role_id = roles[str(inter.channel.id)][str(score)]
                if role_id:
                    
                    role = inter.guild.get_role(role_id)
                    await inter.author.add_roles(role)
                    
                    with open('data.json', 'r') as r_data:
                        
                        j_r_data = json.load(r_data)
                        
                        try:

                            j_r_data[str(inter.channel.id)].append(inter.author.id)
                        
                        except:
                            j_r_data[str(inter.channel.id)] = []
                            j_r_data[str(inter.channel.id)].append(inter.author.id)

                        with open('data.json', "w") as w_data:
                            json.dump(j_r_data, w_data)

                    ending_embed.description = f"You earned {score}/3 points.\nYour rank is {role.name}"
                    await inter.send(embed = ending_embed)
            
            except Exception as e:
                print("Roles doesn't specified", e)
                return
        return

@bot.event
async def on_button_click(interaction):

    if interaction.custom_id == "poll":

        with open("data.json", 'r') as file:

            j_file = json.load(file)
            try:

                if interaction.author.id in j_file[str(interaction.channel.id)]:
                    await interaction.send(content="Excuse me, sir! You already passed this quiz.")
                    return
            except KeyError:
                j_file[str(interaction.channel.id)] = []
                with open('data.json', 'w') as w_file:
                    json.dump(j_file, w_file)

        await interaction.respond(embed = selection_embed_1, components = [
            bot.components_manager.add_callback(
                Select(
                    placeholder = "Select ur answer!",
                    options= [
                        SelectOption(label = "2008", value = "poll1_1"),
                        SelectOption(label = "2009", value = "poll1_2"),
                        SelectOption(label = "2011", value = "poll1_!"),
                        SelectOption(label = "2007", value = "poll1_0")
                    ]
                ),
                next_poll,
            )
        ])

bot.run(cfg.TOKEN)

