import boto3
import os

def aws_connection(region="us-east-1", service="comprehend"):
    client = boto3.client(service, region_name=region)
    return client


def compreend_detect_key_phrases(client, text):
    response = client.detect_key_phrases(
        Text=text,
        LanguageCode=os.environ.get("LANGUAGE", "pt")
    )
    
    for keys in response["KeyPhrases"]:
        print(keys)


def compreend_detect_entities(client, text):
    response = client.detect_entities(
        Text=text,
        LanguageCode=os.environ.get("LANGUAGE", "pt")
    )
    
    for keys in response["Entities"]:
        print(keys)


def main():
    text_to_analyze="""
        Algum tempo hesitei se devia abrir estas memórias pelo princípio ou pelo fim, isto é, se poria em primeiro lugar o meu nascimento ou a minha morte. Suposto o uso vulgar seja co- meçar pelo nascimento, duas considerações me levaram a adotar diferente método: a primeira é que eu não sou propria- mente um autor defunto, mas um defunto autor, para quem a campa foi outro berço; a segunda é que o escrito ficaria assim mais galante e mais novo. Moisés, que também contou a sua morte, não a pôs no intróito, mas no cabo; diferença radical entre este livro e o Pentateuco.        Dito isto, expirei às duas horas da tarde de uma sexta-fei- ra do mês de agosto de 1869, na minha bela chácara de Catumbi. Tinha uns sessenta e quatro anos, rijos e prósperos, era solteiro, possuía cerca de trezentos contos e fui acompa- nhado ao cemitério por onze amigos. Onze amigos! Verdade é que não houve cartas nem anúncios. Acresce que chovia - peneirava - uma chuvinha miúda, triste e constante, tão constante e tão triste, que levou um daqueles fiéis da última hora a intercalar esta engenhosa idéia no discurso que profe- riu à beira de minha cova: -- "Vós, que o conhecestes, meus senhores, vós podeis dizer comigo que a natureza parece es- tar chorando a perda irreparável de um dos mais belos carac- teres que tem honrado a humanidade. Este ar sombrio, estas gotas do céu, aquelas nuvens escuras que cobrem o azul como um crepe funéreo, tudo isso é a dor crua e má que lhe rói à natureza as mais íntimas entranhas; tudo isso é um sublime louvor ao nosso ilustre finado."        Bom e fiel amigo! Não, não me arrependo das vinte apó- lices que lhe deixei. E foi assim que cheguei à cláusula dos meus dias; foi assim que me encaminhei para o undiscovered       country de Hamlet, sem as ânsias nem as dúvidas do moço 
    """
    client = aws_connection()
    # compreend_detect_key_phrases(client, text_to_analyze)

    compreend_detect_entities(client, text_to_analyze)


if __name__ == "__main__":
    main()