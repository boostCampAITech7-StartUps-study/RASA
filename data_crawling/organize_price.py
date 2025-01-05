import pandas as pd
import torch
from unsloth import FastLanguageModel
from tqdm import tqdm


# 모델 및 토크나이저 불러오기
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/Qwen2.5-32B-Instruct-bnb-4bit",
    dtype=None,
    load_in_4bit=True,
    device_map="auto",
)
FastLanguageModel.for_inference(model)


def organize_price(input_file, output_file, model, tokenizer):
    df = pd.read_csv(input_file)
    outputs = []

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Organizing Price"):
        price = row["price"]
        prompt = f"""당신은 팀 단위 스터디룸 예약 서비스의 데이터 분석가입니다. 각기 다른 형식으로 입력된 스터디룸 가격 정보를 팀 단위 사용자가 이해하기 쉽게 정리해주세요.
        
        입력된 가격 정보: {price}

        가격 정보 정리 지침:
        1. 룸 단위의 가격 정보를 최우선으로 추출하여 정리해주세요.
        2. 시간대별 가격을 명확히 구분해주세요 (2시간, 4시간, 6시간 등).
        3. 인원에 따른 룸 구분이 있다면 함께 표시해주세요 (예: 4인실, 6인실).
        4. 정기권이나 시간권 정보는 제외해주세요.
        
        출력 형식 요구사항:
        1. '00인 - 1시간 00,000원' 또는 '0인실 - 1시간 00,000원' 형식으로 작성해주세요.
        2. 주중과 주말/공휴일의 가격정보가 다를 경우 '주중 - 1시간 00,000원, 주말/공휴일 - 1시간 00,000원' 형식으로 작성해주세요.
        3. 시간 당 가격이 변하면, '1,500원~2,500원'과 같은 형식의 범위로 나타내주세요.
        4. 위 조건들의 형식을 벗어났거나, 가격정보가 없다면 '가격정보 없음'이라고 작성해주세요.
        5. 각 가격 정보는 쉼표(,)로 구분해주세요.
        6. 부가 설명이나 기타 정보는 **절대** 포함하지 않습니다. 
        7. 순수 가격 정보만 쉼표로 구분하여 한 줄로 출력해주세요.
        
        예시 출력:
        1인 - 1시간 1,500원, 2시간 2,500원, 3시간 3,500원, 4시간 4,500원
        또는
        4인실 - 2시간 20,000원, 4인실 - 4시간 35,000원, 6인실 - 2시간 30,000원
        또는
        주중 - 1시간 1,000원~2,500원, 주말/공휴일 - 1시간 1,500원~2,500원
        가격정보 없음
        """

        messages = [
            {
                "role": "system",
                "content": "당신은 팀 단위 스터디룸 예약 서비스의 데이터 분석가입니다. 각기 다른 형식으로 입력된 스터디룸 가격 정보를 팀 단위 사용자가 이해하기 쉽게 정리하는 것이 목표입니다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        try:
            input_ids = tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            ).to("cuda")
            # Adjusted generation parameters for more controlled output
            output = model.generate(
                input_ids,
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=128,
                temperature=0.7,  # Added for more controlled generation
                top_p=0.9,  # Added for more controlled generation
            )

            response = tokenizer.decode(output[0], skip_special_tokens=True)

            # Extract the organized price
            organized_price = response.split("assistant")[-1].strip()
            outputs.append(organized_price)
        except Exception as e:
            outputs.append("Organizing Price Failed")
            print(f"Error with prompt: {prompt[:50]}... -> {e}")
        torch.cuda.empty_cache()

    df["orginized_price"] = outputs
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    input_file = "studyroom_df.csv"
    df = pd.read_csv(input_file)
    output_file = "studyroom_df_result.csv"
    organize_price(input_file=input_file, output_file=output_file, model=model, tokenizer=tokenizer)
